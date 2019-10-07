import RPi.GPIO as GPIO
import time
import sys

SIG_DICT = {
    (18, 17): '1',
    (18, 27): '2',
    (18, 22): '3',
    (23, 17): '4',
    (23, 27): '5',
    (23, 22): '6',
    (24, 17): '7',
    (24, 27): '8',
    (24, 22): '9',
    (25, 17): '*',
    (25, 27): '0',
    (25, 22): '#',
}

class Keypad:

    def __init__(self):
        self.rows = [18, 23, 24, 25]
        self.columns = [17, 27, 22 ]
        self.sig_dict = SIG_DICT

    def setup(self):
        ''' Setup the keypad '''
        GPIO.setmode(GPIO.BCM)
        for row_p in self.rows:
            GPIO.setup(row_p, GPIO.OUT)
        for column_p in self.columns:
            GPIO.setup(column_p, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # TODO: Add delay
    def do_polling(self):
        ''' Poll all the keys '''
        time.sleep(0.1)
        for row_p in self.rows:
            GPIO.output(row_p, GPIO.HIGH)
            for column_p in self.columns:
                if GPIO.input(column_p) == GPIO.HIGH:
                    return (row_p, column_p)
            GPIO.output(row_p, GPIO.LOW)
        return None

    def get_next_signal(self):
        ''' Poll all the keys until one is pressed '''
        do_polling = self.do_polling()
        while do_polling is None:
            do_polling = self.do_polling()
        # Gi beskjed til agent om at knapp er trykket ned
        return do_polling

if __name__ == '__main__':
    kp = Keypad()
    kp.setup()
    while(1):
        try:
            print(kp.sig_dict[kp.get_next_signal()])
        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit()
    GPIO.cleanup()
