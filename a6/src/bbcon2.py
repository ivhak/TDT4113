"""
BBCON
"""

import random
import sys
import numpy as np
import wiringpi as wp
from reflectance_sensors import ReflectanceSensors
from ultrasonic import Ultrasonic
from camera import Camera
from motors import Motors
from imager2 import Imager
from RPi import GPIO
from zumo_button import ZumoButton

IMG_WIDTH = 40
IMG_HEIGHT = 96
LOW = 1
MED = 2
HIGH = 3


class BBCON:
    def __init__(self, debug=False):
        self.motor = Motors()
        self.behaviors = []
        self.debug = debug

        self.sensobs = {
            Camera(img_width=IMG_WIDTH, img_height=IMG_HEIGHT): None,
            Ultrasonic(): None,
            ReflectanceSensors(): None
        }
        self.arbitrator = None

    def add_behavior(self, behavior):
        """
        Add behavior to the list of behaviors, set bbcon for the behavior to
        self
        """
        if behavior not in self.behaviors:
            self.behaviors.append(behavior)
            behavior.bbcon = self

    def update_sensobs(self):
        """
        Tell each of the sensobs to update, store the new value in its
        corresponding field in sensobs
        """
        for sensob in self.sensobs.keys():
            sensob.update()
            self.sensobs[sensob] = sensob.value

    def get_sensob_value(self, sensob):
        """
        Get the value of a sensob, by the class of the sensob, i.e.
        to get the last value from camera use
            get_sensob_value(Camera)
        """
        for key, value in self.sensobs.items():
            if isinstance(key, sensob):
                return value

    def add_arbitrator(self, arbitrator):
        """
        Set arbitrator and set the arbitrators bbcon to self
        """
        self.arbitrator = arbitrator
        arbitrator.bbcon = self

    def run_one_timestep(self):
        """
        This runs each iteration.
            1. Update all sensobs
            2. Update all the behaviors with the new values from the sensobs
            3. Arbitrator chooses the next behavior
            4. Run the chosen behaviors motor reccomendations
        """
        self.update_sensobs()
        for behavior in self.behaviors:
            behavior.update()

        chosen_behavior = self.arbitrator.choose_behavior()

        if not self.debug:
            for rec in chosen_behavior.motor_recommendations:
                if chosen_behavior.motor_speed:
                    rec(self.motor, speed=chosen_behavior.motor_speed)
                else:
                    rec(self.motor)

        print("Chose behavior:       {}".format(chosen_behavior))
        print("Chose reccomendation: {}".format(
            chosen_behavior.motor_recommendations))
        print("Chose settings:       {}".format(
            chosen_behavior.motor_speed))


class Behavior:
    """
    Super class for the different behaviors
    """

    def __init__(self):
        self.motor_recommendations = None
        self.motor_speed = None
        self.active_flag = False
        self.halt_request = None
        self.bbcon = None
        self.priority = 0
        self.match_degree = 0
        self.weight = 0

    def consider_deactivation(self):
        if self.active_flag:
            # sjekk om den burde bli satt til inactive
            self.active_flag = False

    def consider_activation(self):
        if not self.active_flag:
            # Sjekke om burde bli satt til aktiv
            self.active_flag = True

    def update(self):
        """
        Act upon the new values from the sensor and recalculate weight
        """
        # if self.active_flag:
        #     self.consider_deactivation()
        # else:
        #     self.consider_activation()
        self.sense_and_act()
        self.update_weight()

    def sense_and_act(self):
        """
        Set new motor recommendations and match degree based upon newest sensor
        values
        """
        pass

    def update_weight(self):
        """
        Calculate the new weight from the newly updated weight
        """
        self.weight = self.match_degree * self.priority


class Avoid(Behavior):
    """
    Uses the ultrasonic sensor to see if there is an object blocking the path
    """

    def __init__(self):
        super().__init__()
        self.priority = MED
        self.motor_recommendations = [Motors.backward]

    def __name__(self):
        return "Avoid"

    def sense_and_act(self):
        value = self.bbcon.get_sensob_value(Ultrasonic)
        self.match_degree = self.calc_match(value)

    def calc_match(self, value):
        return 1 if value < 15 else 0


class WhiteFloor(Behavior):
    """
    Uses the ir sensor to see if there is black tape under the robot
    """

    def __init__(self):
        super().__init__()
        self.priority = HIGH
        self.motor_recommendations = [Motors.backward, Motors.left]
        self.motor_speed = 0.3

    def __name__(self):
        return "WhiteFloor"

    def sense_and_act(self):
        value = self.bbcon.get_sensob_value(ReflectanceSensors)
        # mini = 1
        # index = -1
        print('ReflectanceSensors: ', value)
        # for i, number in enumerate(value):
        #     if number < mini:
        #         mini = number
        #         index = i

        self.match_degree = 0
        # if sum(value)/len(value) < 0.5:
        if min(value) < 0.2:
            self.match_degree = 1

        # self.match_degree = self.calc_match(mini)

        # if index == 0 or index == 1:
        #     self.motor_recommendations = Motors.right  #
        # elif index == 5 or index == 4:
        #     self.motor_recommendations = Motors.left
        # elif index == -1:
        #     self.motor_recommendations = Motors.forward
        # else:

    def calc_match(self, maks):
        return 1 - maks


class FindRed(Behavior):
    """
    Uses the camera to find out if there is a red object in front of the robot
    """

    def __init__(self, sensob=None, debug=False):
        super().__init__()
        self.priority = MED
        self.debug = debug
        self.imager = Imager(width=IMG_WIDTH, height=IMG_HEIGHT)
        self.motor_recommendations = [Motors.forward]

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

        if ratio > 0.5:
            self.match_degree = 0.8
            self.motor_speed = 1
        else:
            self.match_degree = 0
            self.motor_speed = 0.3


class Default(Behavior):
    """
    If none of the other behaviors need to act, we default to doing something
    random
    """

    def __init__(self):
        super().__init__()
        self.priority = LOW
        self.weight = 1
        self.match_degree = 1
        self.motor_recommendations = [Motors.forward, None]

    def __name__(self):
        return "Default"

    def sense_and_act(self):
        self.motor_recommendations[1] = random.choice(
            [Motors.forward, Motors.left, Motors.right]
        )


class Arbitrator:

    def __init__(self):
        self.bbcon = None

    def choose_behavior(self):
        chosen_behavior = None
        maks = 0
        for behavior in self.bbcon.behaviors:
            print("{}: {}".format(behavior.__name__(), behavior.weight))
            if behavior.weight > maks:
                maks = behavior.weight
                chosen_behavior = behavior
        return chosen_behavior


def main():
    GPIO.setwarnings(False)
    wp.wiringPiSetupGpio()
    bbcon = BBCON(debug=False)
    bbcon.add_behavior(FindRed())
    bbcon.add_behavior(Avoid())
    bbcon.add_behavior(WhiteFloor())
    bbcon.add_behavior(Default())
    bbcon.add_arbitrator(Arbitrator())

    ZumoButton().wait_for_press()

    try:
        while True:
            bbcon.run_one_timestep()
    except KeyboardInterrupt:
        bbcon.motor.stop()
        sys.exit("Stopping motors")


if __name__ == '__main__':
    main()
