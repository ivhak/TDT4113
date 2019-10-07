import RPi.GPIO as GPIO
import time

class LED:
    def __init__(self):
        self.pins = [16, 12, 20]

        self.pin_led_states = [
            [1, 0, -1], # A
            [0, 1, -1], # B
            [-1, 1, 0], # C
            [-1, 0, 1], # D
            [1, -1, 0], # E
            [0, -1, 1]  # F
        ]

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        self.set_pin(0, -1)
        self.set_pin(1, -1)
        self.set_pin(2, -1)

    def set_pin(self, pin_index, pin_state):
        if pin_state == -1:
            GPIO.setup(self.pins[pin_index], GPIO.IN)
        else:
            GPIO.setup(self.pins[pin_index], GPIO.OUT)
            GPIO.output(self.pins[pin_index], pin_state)

    def light_led(self, led_num):
        for pin_index, pin_state in enumerate(self.pin_led_states[led_num]):
            self.set_pin(pin_index, pin_state)

    def flash_all_leds(self):
        pass

    def twinkle_all_leds(self):
        pass

if __name__ == '__main__':
    lb = LED()
    lb.setup()
    for i in range(6):
        time.sleep(1)
        lb.light_led(i)

    GPIO.cleanup()
