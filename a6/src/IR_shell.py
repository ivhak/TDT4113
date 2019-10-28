from time import sleep
import random
import imager2 as IMR
from reflectance_sensors import ReflectanceSensors
from camera import Camera
from motors import Motors
from ultrasonic import Ultrasonic
from zumo_button import ZumoButton


def explorer(dist=10):
    ZumoButton().wait_for_press()
    m = Motors()
    u = Ultrasonic()
    print(u.sensor_get_value())
    while u.sensor_get_value() > dist:
        m.forward(.2, 0.2)
        print(u.value)
    m.backward(.1, .5)
    m.left(.5,3)
    m.right(.5, 3.5)
    sleep(2)
    while u.sensor_get_value() < dist*5:
        m.backward(.2, 0.2)
    m.left(.75, 5)

def main():
    explorer()

if __name__ == "__main__":
    main()

