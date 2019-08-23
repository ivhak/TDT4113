'''
This file provides a few of the 'tricky' elements of the Morse Code
project: those involving setting up and reading from the serial port.

IMPORTANT!! If you are a MAC user, you will need to modify the actual device
code for your serial port in arduino_connect.py
'''

# This is the key import so that you can access the serial port.
import arduino_connect


# Codes for the 4 signals sent to this level from the Arduino

_dot = 1
_dash = 2
_mpause = 3
_lpause = 4

_morse_codes = {
        '12':     'a',
        '2111':   'b',
        '2121':   'c',
        '211':    'd',
        '1':      'e',
        '1121':   'f',
        '221':    'g',
        '1111':   'h',
        '11':     'i',
        '1222':   'j',
        '212':    'k',
        '1211':   'l',
        '22':     'm',
        '21':     'n',
        '222':    'o',
        '1221':   'p',
        '2212':   'q',
        '121':    'r',
        '111':    's',
        '2':      't',
        '112':    'u',
        '1112':   'v',
        '122':    'w',
        '2112':   'x',
        '2122':   'y',
        '2211':   'Z',
        '22222':  '1',
        '12222':  '2',
        '11222':  '2',
        '11122':  '3',
        '11112':  '4',
        '11111':  '5',
        '21111':  '6',
        '22111':  '7',
        '22211':  '8',
        '22221':  '9'
}


# Morse Code Class
class mocoder():

    # This is where you set up the connection to the serial port.
    def __init__(self, sport=True):
        if sport:
            self.serial_port = arduino_connect.basic_connect()
        self.reset()

    def reset(self):
        self.current_message = ''
        self.current_word = ''
        self.current_symbol = ''

    # This should receive an integer in range 0-3 from the Arduino via a serial
    # port
    def read_one_signal(self, port=None):
        connection = port if port else self.serial_port
        while True:
            # Reads the input from the arduino serial connection
            data = connection.readline()
            if data:
                return data

    # The signal returned by the serial port is one (sometimes 2) bytes, that
    # represent characters of a string.  So, a 2 looks like this: b'2', which
    # is one byte whose integer value is the ascii code 50 (ord('2') = 50).
    # The use of function 'int' on the string converts it automatically.   But,
    # due to latencies, the signal sometimes consists of 2 ascii codes, hence
    # the little for loop to cycle through each byte of the signal.

    def decoding_loop(self):
        while True:
            s = self.read_one_signal(self.serial_port)
            print(s)
            # for byte in s:
            #     self.process_signal(int(chr(byte)))

    def process_signal(self, sig):
        if (sig == _dot or sig == _dash):
            self.current_symbol += str(sig)
        if (sig == _mpause):
            self.current_word += _morse_codes[self.current_symbol]
            self.current_symbol = ''
        if (sig == _lpause):
            self.current_message += self.current_word + ' '
            self.current_word = ''
        return True


'''
To test if this is working, do the following in a Python command window:

> from morse_skeleton import *
> m = mocoder()
> m.decoding_loop()

If your Arduino is currently running and hooked up to the serial port, then
this simple decoding loop will print the raw signals that the Arduino sends to
the serial port.  Each time you press (or release) your morse-code device, a
signal should appear in your Python window. In Python, these signals typically
look like this: b'5' or b'1' or b'3', etc.
'''

if __name__ == '__main__':
    m = mocoder()
    m.decoding_loop()
