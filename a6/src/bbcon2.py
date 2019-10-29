"""
BBCON
"""
from reflectance_sensors import ReflectanceSensors
from ultrasonic import Ultrasonic
from camera import Camera
from motors import Motors

IMG_WIDTH = 40
IMG_HEIGHT = 96


class BBCON:
    def __init__(self):
        self.motor = Motors()
        self.sensobs = {
            Camera(img_width=IMG_WIDTH, img_height=IMG_HEIGHT): None,
            Ultrasonic(): None,
            ReflectanceSensors(): None
        }

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
