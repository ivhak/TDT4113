"""
BBCON
"""

import random
import time
from ultrasonic import Ultrasonic
import motors
from camera import Camera
from imager2 import Imager
from zumo_button import ZumoButton
import numpy as np
import wiringpi as wp
from reflectance_sensors import ReflectanceSensors

IMG_WIDTH = 40
IMG_HEIGHT = 96


class BBCON:

    def __init__(self):
        self.behaviors = []
        self.active_behaviors = []
        self.sensobs = Sensobs()
        self.motobs = []
        self.arbitrator = None
        self.halt = False

    def add_behavior(self, behavior):
        """append a newly-created behavior onto the behaviors list"""
        if behavior not in self.behaviors:
            self.behaviors.append(behavior)
            behavior.bbcon = self

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
            for behav in self.behaviors:
                behav.update()

            motor_rec, halt, behavior = self.arbitrator.choose_action()
            self.halt = halt

            for motor in self.motobs:
                motor.update(motor_rec)

            # Får en pause sånn at motorene får kjørt litt før neste handling.
            time.sleep(0.5)

            for sensob in self.sensobs:
                sensob.reset()


class Sensobs:

    def __init__(self):
        self.sensors = {
            'camera': Camera(img_width=IMG_WIDTH, img_height=IMG_HEIGHT),
            'ultrasonic': Ultrasonic(),
            'reflectance': ReflectanceSensors()
        }
        self.values = {
            'camera': None,
            'ultrasonic': None,
            'reflectance': None,
        }

    def update(self):
        for name, sensor in self.sensors.items():
            sensor.update()
            new_value = sensor.get_value()
            self.values[name] = new_value

    def get_value(self, sensor):
        return self.values[sensor]

    def reset(self):
        for key in self.values.keys():
            self.values[key] = None


class Motob:

    def __init__(self, motors):
        self.motors = motors
        self.value = 0
        wp.wiringPiSetupGpio()

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

    def __init__(self):
        self.sensobs = None
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

    def __init__(self):
        self.priority = 3
        self.sensobs = [ReflectanceSensors()]

    def sense_and_act(self):
        # Value er en array
        value = self.sensobs.value
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
            self.motor_recommendations = 1  # [1, 0]#motors.right(0.25, 5)
        elif index == 5 or index == 4:
            self.motor_recommendations = 2  # [0, 1]#motors.left(0.25, 5)
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

    def __init__(self):
        self.priority = 1
        self.sensobs = [Ultrasonic()]

    def sense_and_act(self):
        value = self.sensobs.value[0]
        print("Value is ", value)
        degree = self.calc_mach()
        # Da vil vi at roboten skal rygge
        self.motor_recommendations = 4  # self.motors.backward()
        # Evt halt-req
        return degree, self.motor_recommendations

    def calc_macth(self, value):
        degree = 1/value
        return degree



class FindRed(Behavior):
    """
    This behaviour advices the robot to accelerate whenever the camera spots
    something red.
    """

    def __init__(self, sensob=None, debug=False):
        self.priority = 1
        self.debug = debug
        self.imager = Imager(width=IMG_WIDTH, height=IMG_HEIGHT)
        super().__init__()

    def sense_and_act(self):
        """
        Take a picture, find the percentage of red pixels
        """

        def red_only(p):
            """
            Maps red pixels to white, everything else to black
            """
            lower = (155, 25, 0)
            upper = (255, 100, 100)
            # r, g, b = p
            # if (lower[0] <= r <= upper[0] and
            #     lower[1] <= g <= upper[1] and
            #         lower[2] <= b <= upper[2]):
            #     return (255, 255, 255)
            if lower <= p <= upper:
                return (255, 255, 255)
            return (0, 0, 0)

        image = self.bbcon.sensobs.values['camera']
        mapped = self.imager.map_image2(red_only, image=image)

        if self.debug:
            mapped.dump_image(fid='image_mapped', type='png')

        im_arr = np.array(mapped.image)
        white_pixels = np.sum(im_arr == (255, 255, 255))

        ratio = white_pixels/(len(im_arr[0])*len(im_arr))

        return 0.8 if ratio > 0.05 else 0, 5


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

    # bbcon = BBCON()
    # bbcon.add_behavior(FindRed())
    # bbcon.add_behavior(Avoid())

    # motor = motors.Motors()
    # # motor.forward(0.5, 2.0)
    # motobs = Motob(motor)
    # sensor = rs.ReflectanceSensors()
    # sensor.calibrate()
    # print("Sensorverdi ", sensor.get_value())
    # sensor2 = us.Ultrasonic()
    # # bbcon = BBCON()
    # sensorer = [sensor2]
    # sensob = Sensobs(sensorer)
    # sensob.update()
    # print("Sensorverdi ", sensob.value)
    '''
    bbcon.add_sensob(sensob)
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

    white = WhiteFloor(bbcon, sensob)
    avoid = Avoid()
    red = FindRed()
    bbcon.add_behavior(white)
    bbcon.add_behavior(avoid)
    bbcon.add_behavior(red)
    while bbcon.halt is False:
    bbcon.run_one_timestep()
    print(sensob.value)
    print(sensob.value)
    '''


# main()
