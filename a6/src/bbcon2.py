"""
BBCON
"""
from reflectance_sensors import ReflectanceSensors
from ultrasonic import Ultrasonic
from camera import Camera
import motors as m
from imager2 import Imager
from RPi import GPIO
import numpy as np

IMG_WIDTH = 40
IMG_HEIGHT = 96


class BBCON:
    def __init__(self):
        self.motor = m.Motors()
        self.behaviors = []
        self.sensobs = {
            Camera(img_width=IMG_WIDTH, img_height=IMG_HEIGHT): None,
            Ultrasonic(): None,
            ReflectanceSensors(): None
        }
        self.arbitrator = None

    def add_behavior(self, behavior):
        if behavior not in self.behaviors:
            self.behaviors.append(behavior)
            behavior.bbcon = self

    def update_sensobs(self):
        for sensob in self.sensobs.keys():
            sensob.update()
            self.sensobs[sensob] = sensob.value

    def get_sensob_value(self, sensob):
        for key, value in self.sensobs.items():
            if isinstance(key, sensob):
                return value

    def add_arbitrator(self, arbitrator):
        self.arbitrator = arbitrator
        arbitrator.bbcon = self

    def run_one_timestep(self):
        self.update_sensobs()
        for behavior in self.behaviors:
            behavior.update()

        chosen_behavior = self.arbitrator.choose_behavior()
        chosen_behavior.motor_recommendations(self.motor)


class Behavior:
    def __init__(self):
        self.motor_recommendations = None
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
        self.sense_and_act()
        self.update_weight()

    def sense_and_act(self):
        pass

    def update_weight(self):
        self.weight = self.match_degree * self.priority

    def get_motor_rec(self):
        return self.motor_recommendations

    def get_w(self):
        return self.weight


class Avoid(Behavior):
    def __init__(self):
        self.priority = 1
        super().__init__()

    def __name__(self):
        return "Avoid"

    def sense_and_act(self):
        value = self.bbcon.get_sensob_value(Ultrasonic)
        print("Value is ", value)
        self.match_degree = self.calc_match(value)
        self.motor_recommendations = m.backward

    def calc_match(self, value):
        return 1/value if value else 0


class WhiteFloor(Behavior):
    def __init__(self):
        self.priority = 3
        super().__init__()

    def __name__(self):
        return "WhiteFloor"

    def sense_and_act(self):
        value = self.bbcon.get_sensob_value(ReflectanceSensors)
        maks = 350
        index = -1
        for number in value:
            if number > maks:
                maks = number
                index = value[number]
        self.match_degree = self.calc_match(value, maks)

        if index == 0 or index == 1:
            self.motor_recommendations = m.right  #
        elif index == 5 or index == 4:
            self.motor_recommendations = m.left
        elif index == -1:
            self.motor_recommendations = m.forward
        else:
            self.motor_recommendations = m.backward

    def calc_match(self, value, maks):
        diff = maks - 350
        degree = diff / 650  # 2000 skal den få veldig høy degree
        return degree


class FindRed(Behavior):
    """
    This behavior advices the robot to accelerate whenever the camera spots
    something red.
    """

    def __init__(self, sensob=None, debug=False):
        self.priority = 1
        self.debug = debug
        self.motor_recommendations = m.forward()
        self.motor_settings = (0.5, 4)
        self.imager = Imager(width=IMG_WIDTH, height=IMG_HEIGHT)
        super().__init__()

    def __name__(self):
        return "FindRed"

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
            r, g, b = p
            if (lower[0] <= r <= upper[0] and
                lower[1] <= g <= upper[1] and
                    lower[2] <= b <= upper[2]):
                return (255, 255, 255)
            return (0, 0, 0)

        image = self.bbcon.get_sensob_value(Camera)
        mapped = self.imager.map_image2(red_only, image=image)

        if self.debug:
            mapped.dump_image(fid='image_mapped', type='png')

        im_arr = np.array(mapped.image)
        white_pixels = np.sum(im_arr == (255, 255, 255))

        ratio = white_pixels/(len(im_arr[0])*len(im_arr))

        self.match_degree = 0.8 if ratio > 0.5 else 0
        self.motor_recommendations = m.forward



class Arbitrator:

    def __init__(self):
        self.bbcon = None
        self.motor_recommendation = m.forward

    def choose_behavior(self):
        chosen_behavior = None
        maks = 0
        for behavior in self.bbcon.behaviors:
            if behavior.weight >= maks:
                chosen_behavior = behavior
        return chosen_behavior




def main():
    GPIO.setwarnings(False)
    bbcon = BBCON()
    bbcon.add_behavior(FindRed(debug=True))
    bbcon.add_behavior(Avoid())
    bbcon.add_behavior(WhiteFloor())
    bbcon.run_one_timestep()


if __name__ == '__main__':
    main()
