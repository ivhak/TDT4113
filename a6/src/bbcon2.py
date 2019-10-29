"""
BBCON
"""
from reflectance_sensors import ReflectanceSensors
from ultrasonic import Ultrasonic
from camera import Camera
from motors import Motors
from imager2 import Imager
import numpy as np

IMG_WIDTH = 40
IMG_HEIGHT = 96


class BBCON:
    def __init__(self):
        self.motor = Motors()
        self.behaviors = []
        self.sensobs = {
            Camera(img_width=IMG_WIDTH, img_height=IMG_HEIGHT): None,
            Ultrasonic(): None,
            ReflectanceSensors(): None
        }

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

    def run_one_timestep(self):
        self.update_sensobs()
        for behavior in self.behaviors:
            behavior.update()


class Behavior:
    def __init__(self):
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


class FindRed(Behavior):
    """
    This behavior advices the robot to accelerate whenever the camera spots
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

        return 0.8 if ratio > 0.05 else 0, 5


def main():
    bbcon = BBCON()
    bbcon.add_behavior(FindRed(debug=True))
    bbcon.run_one_timestep()


if __name__ == '__main__':
    main()
