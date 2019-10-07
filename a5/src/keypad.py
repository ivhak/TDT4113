'''
The Raspberry Pi is connected to a keypad with four rows and three columns:
        +---+---+---+
        | 1 | 2 | 3 |
        +---+---+---+
        | 4 | 5 | 6 |
        +---+---+---+
        | 7 | 8 | 9 |
        +---+---+---+
        | * | 0 | # |
        +---+---+---+
When KPC is queried for a signal, each row and column are polled. If row
i and column j are HIGH, the value (i,j) is translated to the symbol on
the keypad, as defined in SIG_DICT.

There are seven connectors to the board, and they are mapped as such
(from left to right):

        Row 1: R0 -> 18
        Row 2: R1 -> 23
        Row 3: R2 -> 24
        Row 4: R3 -> 25
        Col 1: R4 -> 17
        Col 2: R5 -> 27
        Col 3: R6 -> 22
'''

import time
import sys
import RPi.GPIO as GPIO

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
    ''' Interpret and translate keypad input '''

    def __init__(self):
        self.rows = [18, 23, 24, 25]
        self.columns = [17, 27, 22]
        self.sig_dict = SIG_DICT

    def setup(self):
        ''' Setup the keypad '''
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for row_p in self.rows:
            GPIO.setup(row_p, GPIO.OUT)
        for column_p in self.columns:
            GPIO.setup(column_p, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def do_polling(self):
        ''' Poll all the keys '''
        time.sleep(0.2)
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
        return self.sig_dict[do_polling]


def main():
    ''' Test  keypad '''
    keypad = Keypad()
    keypad.setup()
    while True:
        try:
            print(keypad.get_next_signal())
        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit()
    GPIO.cleanup()


if __name__ == '__main__':
    main()
