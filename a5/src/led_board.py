'''
The LED board is Charlieplexed such that 6 LED can be controlled by 3 pins.
The LEDs are set up like this:
    0  2  4
    1  3  5
'''

import time
import RPi.GPIO as GPIO


class LED:
    ''' Control the Charlieplexed LED board '''
    def __init__(self):
        self.pins = [16, 12, 20]

        self.pin_led_states = [
            [0, 1, -1],  # 1
            [1, 0, -1],  # 2
            [-1, 1, 0],  # 3
            [-1, 0, 1],  # 4
            [1, -1, 0],  # 5
            [0, -1, 1]   # 6
        ]

    def setup(self):
        ''' Setup LED board '''
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.all_off()

    def all_off(self):
        ''' Turn of all LEDs '''
        self.set_pin(0, -1)
        self.set_pin(1, -1)
        self.set_pin(2, -1)

    def set_pin(self, pin_index, pin_state):
        ''' Set pin <pin_index> to <pin_state> '''
        if pin_state == -1:
            GPIO.setup(self.pins[pin_index], GPIO.IN)
        else:
            GPIO.setup(self.pins[pin_index], GPIO.OUT)
            GPIO.output(self.pins[pin_index], pin_state)

    def light_led(self, led_num, dur=None):
        ''' Light led number <led_num> for <dur> seconds '''
        for pin_index, pin_state in enumerate(self.pin_led_states[led_num]):
            self.set_pin(pin_index, pin_state)
        if dur is not None:
            time.sleep(dur)
        self.all_off()

    def startup_show(self):
        ''' Light show for startup '''
        for _ in range(4):
            for i in [2, 3]:
                self.light_led(i, dur=0.2)

    def shutdown_show(self):
        ''' Light show for shutdown '''
        for _ in range(4):
            for i in [0, 1, 4, 5]:
                self.light_led(i, dur=0.2)

    def flash_all_leds(self, seconds):
        '''
        Flash all leds on and off for <seconds> seconds.
        Due to the Charlieplexing, several LEDs can not be
        lit at the same time, but we can try.
        '''
        start_t = time.time()
        state = True
        while time.time() - start_t < seconds:
            state = not state
            if state:
                for i in range(6):
                    time.sleep(0.03)
                    self.light_led(i)
            self.all_off()
            time.sleep(0.5)

    def twinkle_all_leds(self, seconds):
        ''' Light one led at a time for <seconds> seconds '''
        start_t = time.time()
        while time.time() - start_t < seconds:
            for i in range(6):
                self.light_led(i)
                time.sleep(0.2)
        self.all_off()


def main():
    ''' Test LED board '''
    led_board = LED()
    led_board.setup()
    led_board.flash_all_leds(5)
    led_board.twinkle_all_leds(10)
    for i in range(6):
        time.sleep(1)
        led_board.light_led(i)
    GPIO.cleanup()


if __name__ == '__main__':
    main()
