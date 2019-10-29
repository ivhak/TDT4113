"""
BBCON. yoyoyoyo
Mikkel sier: Har jeg fått det til nå?
Giske: jeg klarte det!
"""
import random
import time
import ultrasonic as us
import motors
from camera import Camera
from imager2 import Imager
from zumo_button import ZumoButton
import numpy as np
import wiringpi as wp
import reflectance_sensors as rs


class BBCON:

    def __init__(self):
        self.behaviors = []
        self.active_behaviors = []
        self.sensobs = []
        self.motobs = []
        self.arbitrator = None
        self.halt = False

    def add_behavior(self, behavior):
        """append a newly-created behavior onto the behaviors list"""
        if behavior not in self.behaviors:
            self.behaviors.append(behavior)

    def add_sensob(self, sensob):
        """append a newly-created sensob onto the sensobs list"""
        if sensob not in self.sensobs:
            self.sensobs.append(sensob)

    def add_motob(self, motob):
        self.motobs = motob

    def activate_behavior(self, behavior):
        """add an existing behavior onto the active-behaviors list."""
        if behavior in self.behaviors:
            self.active_behaviors.append(behavior)

    def deactivate_behavior(self, behavior):
        """Remove an existing behavior from the active behaviors list."""
        if behavior in self.active_behaviors:
            self.active_behaviors.remove(behavior)

    def run_one_timestep(self):

        while not self.halt:
            for sensob in self.sensobs:
                sensob.update()

            for behav in self.behaviors:
                behav.update()

            motor_rec, halt, behavior = self.arbitrator.choose_action()
            self.halt = halt
            print("Zumoen har blitt haltet")

            for motor in self.motobs:
                motor.update(motor_rec)

            time.sleep(0.5)  # Får en pause sånn at motorene får kjørt litt før neste handling.

            for sensob in self.sensobs:
                sensob.reset()


class Sensobs:

    def __init__(self, sensors):
        self.sensors = sensors
        self.value = []

    def update(self):
        for sensor in self.sensors:
            sensor.update()
            newValue = sensor.get_value()
            self.value.append(newValue)

    def get_value(self):
        return self.value

    def reset(self):
        self.value = []


class Motob:

    def __init__(self, motors):
        self.motors = motors
        self.value = 0
        # wp.wiringPiSetupGpio()

    def update(self, value):
        self.set_value(value)
        print("Self.value ", self.value)
        self.operationalize(self.value)

    def operationalize(self, value):
        if value == 1:
            self.motors.right(dur=1)
        elif value == 2:
            self.motors.left(dur=1)
        elif value == 4:
            self.motors.backward(dur=1)
        elif value == 5:
            self.motors.forward(dur=4)
        else:
            self.motors.forward(dur=1)
        # self.motors.set_left_dir(value[0])
        # self.motors.set_right_dir(value[1])

        # self.motors[0].set_value(value[0])
        # self.motors[1].set_value(value[1])

    def set_value(self, value):
        self.value = value


class Behavior:

    def __init__(self, bbcon, sensobs):
        self.bbcon = bbcon
        self.sensobs = sensobs
        self.motor_recommendations = []
        self.active_flag = False
        self.halt_request = None  # ??
        self.priority = 0
        self.match_degree = 0  # Regnes ut i fra
        self.weight = 0  # self.match_degree * pri

    def consider_deactivation(self):
        if self.active_flag:
            # sjekk om den burde bli satt til inactive
            self.active_flag = False

    def consider_activation(self):
        if not self.active_flag:
            # Sjekke om burde bli satt til aktiv
            self.active_flag = True

    def update(self):
        if self.active_flag:
            self.consider_deactivation()
        else:
            self.consider_activation()
        self.match_degree, self.halt_request = self.sense_and_act()
        self.update_weight()
        return self.match_degree, self.halt_request

    def sense_and_act(self):
        pass

    def update_weight(self):
        self.weight = self.match_degree * self.priority

    def get_motor_rec(self):
        return self.motor_recommendations

    def get_w(self):
        return self.weight


class WhiteFloor(Behavior):
    """Roboten skal holde seg innenfor de svarte strekene.
    Denne oppførelen har pri = 1"""

    """IR-sensor gir ut en array [0,..., 5], med verdier fra 0-2000. 
    0 er hvit, og 2000 er svart"""

    def __init__(self, bbcon, sensob):
        super().__init__(bbcon, sensob)
        self.priority = 3

    def sense_and_act(self):
        # Value er en array

        original_value = self.sensobs.value
        value = original_value[0:4]


        maks = 350
        index = -1
        for number in value:
            if number > maks:
                maks = number
                index = value[number]
        degree = self.calc_match(value, maks)
        # Da vil vi at roboten skal rygge
        print("MOTORS ER ", motors)

        if index == 0 or index == 1:
            self.motor_recommendations = 1 #[1, 0]#motors.right(0.25, 5)
        elif index == 4:
            self.motor_recommendations = 2 #[0, 1]#motors.left(0.25, 5)
        elif index == -1:
            self.motor_recommendations = 3  # [1, 1]#motors.forward(0.25, 5)
        else:
            self.motor_recommendations = 4  # [-1, -1]#motors.backward(0.25, 5)
        # Evt halt-req
        return degree, self.motor_recommendations

    def calc_match(self, value, maks):
        diff = maks - 350
        degree = diff / 650  # 2000 skal den få veldig høy degree
        return degree



class Avoid(Behavior):
    """Roboten skal unngå hindringer.
    Denne oppførselen har pri = 2"""

    """Antar at høy verdi(600) er nærme"""

    def __init__(self, bbcon, sensobs):
        super().__init__(bbcon, sensobs)
        self.priority = 1

    def sense_and_act(self):
        value = self.sensobs.value[0]
        print("Value is ", value)
        degree = self.calc_mach()
        # Da vil vi at roboten skal rygge
        self.motor_recommendations = 4  # self.motors.backward()
        # Evt halt-req
        return degree, self.motor_recommendations

    def calc_mach(self, value):
        degree = 1/value
        return degree


class FindRed(Behavior):
    """Roboten skal finne de røde tingene vi har plassert ut.
    Denne har pri = 3"""

    def __init__(self, bbcon=None, sensob=None):

        self.camera = Camera(img_width=40, img_height=96)
        self.imager = Imager(width=40, height=96)
        self.priority = 1
        super().__init__(bbcon, sensob)

    def sense_and_act(self):
        """
        Take a picture, find the percentage of red pixels
        """

        def red_only(p):
            lower = (155, 25, 0)
            upper = (255, 100, 100)
            r, g, b = p
            if (lower[0] <= r <= upper[0] and
                lower[1] <= g <= upper[1] and
                    lower[2] <= b <= upper[2]):
                return (255, 255, 255)
            return (0, 0, 0)

        self.camera.update()
        image = self.camera.value
        mapped = self.imager.map_image2(red_only, image=image)
        mapped.dump_image(fid='image_mapped', type='png')

        im_arr = np.array(mapped.image)
        mask = im_arr == [255, 255, 255]
        white_pixels = np.sum(mask)
        ratio = white_pixels/(len(im_arr[0])*len(im_arr))

        return (0.8 if ratio > 0.05 else 0, 5)

    def calc_match(self, value):
        return value


class Arbitrator:

    def __init__(self, behaviors):
        self.behaviors = behaviors
        self.halt = False
        self.motor_rec = [0, 0]

    def choose_action(self):
        tot = 0
        weights = []
        for i in range(0, 3):
            weights.append(self.behaviors[i].get_w())
        for weight in weights:
            tot += weight
        choose = random.uniform(0, tot)
        print("weights ", weights)
        en = weights[0]
        to = weights[0]+weights[1]
        tre = weights[0]+weights[1]+weights[2]
        choose_list = [en, to, tre]
        behavior = None
        if choose <= choose_list[0]:
            self.motor_rec = self.behaviors[0].get_motor_rec()
            behavior = self.behaviors[0]
        elif choose <= choose_list[1]:
            self.motor_rec = self.behaviors[1].get_motor_rec()
            behavior = self.behaviors[1]
        else:
            self.motor_rec = self.behaviors[2].get_motor_rec()
            self.halt = True
            behavior = self.behaviors[2]
        return self.motor_rec, self.halt, behavior


def main():
    motor = motors.Motors()
    #motor.forward(0.5, 2.0)
    motobs = Motob(motor)
    sensor = rs.ReflectanceSensors()
    sensor.calibrate()
    print("Sensorverdi ", sensor.get_value())
    sensor2 = us.Ultrasonic()
    #bbcon = BBCON()
    sensorer = [sensor2]
    sensob = Sensobs(sensorer)
    sensob.update()
    print("Sensorverdi ", sensob.value)
    '''bbcon.add_sensob(sensob)
    bbcon.add_motob(motobs)
    avoid = Avoid(bbcon, sensob)
    x, y = avoid.update()  # sense_and_act()
    print("Vil velge ", y)
    print("Degree ", x)
    print("TEST ", avoid.match_degree)
    print("Avoid weight ", avoid.get_w())
    bbcon.add_behavior(avoid)
    print("Behavior ", bbcon.behaviors)
    avoid1 = Avoid(bbcon, sensob)
    avoid2 = Avoid(bbcon, sensob)
    behaviors = [avoid1, avoid, avoid2]
    arb = Arbitrator(behaviors)
    choose, halt = arb.choose_action()
    print("Choose ", choose, " halt ", halt)
    motobs.update(choose)

    # arbi =
    #white = WhiteFloor(bbcon, sensob)
    #avoid = Avoid()
    #red = FindRed()
    # bbcon.add_behavior(white)
    # bbcon.add_behavior(avoid)
    # bbcon.add_behavior(red)
    # while bbcon.halt is False:
    #    bbcon.run_one_timestep()
    # print(sensob.value)
    #print(sensob.value)'''



# main()
