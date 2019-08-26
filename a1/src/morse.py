import sys
import arduino_connect


# Codes for the 4 signals sent to this level from the Arduino
_dot = 1
_dash = 2
_mpause = 3
_lpause = 4


# Morse Code Class
class mocoder():

    # Morse codes are decoded with 1's and 2's instead of 0's and 1's to avoid
    # sending "false" values from the Arduino:
    #       1  :  DOT  :  .
    #       2  :  DASH :  -
    _morse_codes = {
            '12':     'a',  # .-
            '2111':   'b',  # -...
            '2121':   'c',  # -.-.
            '211':    'd',  # -..
            '1':      'e',  # .
            '1121':   'f',  # ..-.
            '221':    'g',  # --.
            '1111':   'h',  # ....
            '11':     'i',  # ..
            '1222':   'j',  # .---
            '212':    'k',  # -.-
            '1211':   'l',  # .-..
            '22':     'm',  # --
            '21':     'n',  # -.
            '222':    'o',  # ---
            '1221':   'p',  # .--.
            '2212':   'q',  # --.-
            '121':    'r',  # .-.
            '111':    's',  # ...
            '2':      't',  # -
            '112':    'u',  # .--
            '1112':   'v',  # ...-
            '122':    'w',  # .--
            '2112':   'x',  # -..-
            '2122':   'y',  # -.--
            '2211':   'Z',  # --.-
            '22222':  '0',  # -----
            '12222':  '1',  # .----
            '11222':  '2',  # ..---
            '11122':  '3',  # ...--
            '11112':  '4',  # ....-
            '11111':  '5',  # .....
            '21111':  '6',  # -....
            '22111':  '7',  # --...
            '22211':  '8',  # ---..
            '22221':  '9'   # ----.
    }

    # This is where you set up the connection to the serial port.
    # If no port is given when initiating, e.g. mocoder(arport=some_port),
    # self.serial_port defaults to '/dev/ttyUSB0' (the default device dev path
    # on linux)
    def __init__(self, sport=None):
        if sport is None:
            self.serial_port = arduino_connect.basic_connect()
        else:
            self.serial_port = arduino_connect.basic_connect(arport=sport)
        self.reset()

    def reset(self):
        self.current_word = ''
        self.current_symbol = ''

    # This should receive an integer in range 1-4 from the Arduino via a serial
    # port:
    #       1  :  DOT
    #       2  :  DASH
    #       3  :  MPAUSE (letter pause)
    #       4  :  LPAUSE (word pause)
    def read_one_signal(self, port=None):
        connection = port if port else self.serial_port
        while True:
            # Reads the input from the arduino serial connection
            data = connection.readline()
            if data:
                return data

    # Add next byte from the stream to the current symbol
    def update_current_symbol(self, signal):
        self.current_symbol += signal

    # Add decoded letter to current word
    def update_current_word(self, letter):
        self.current_word += letter

    # Handle MPAUSE signal: Decode current symbol and update current word
    def handle_symbol_end(self):
        letter = self._morse_codes.get(self.current_symbol, '')
        self.update_current_word(letter)
        self.current_symbol = ''

    # handle LPAUSE signal: End current word and print it
    def handle_word_end(self):
        self.handle_symbol_end()
        print(self.current_word)
        self.current_word = ''

    def process_signal(self, sig):
        if (sig == _dot or sig == _dash):
            self.update_current_symbol(str(sig))
        elif (sig == _mpause):
            self.handle_symbol_end()
        elif (sig == _lpause):
            self.handle_word_end()

    # The signal returned by the serial port is one (sometimes 2) bytes, that
    # represent characters of a string.  So, a 2 looks like this: b'2', which
    # is one byte whose integer value is the ascii code 50 (ord('2') = 50).
    # The use of function 'int' on the string converts it automatically.   But,
    # due to latencies, the signal sometimes consists of 2 ascii codes, hence
    # the little for loop to cycle through each byte of the signal.
    def decoding_loop(self):
        while True:
            s = self.read_one_signal(self.serial_port)
            for byte in s:
                self.process_signal(int(chr(byte)))


# Run this program with either just:
#           python3 morse.py
# to use the default serial port '/dev/ttyUSB0'.
# Alternatively, to use a different serial porty:
#           python4 morse.py <serial_port>
def main():
    port = None
    if (len(sys.argv[1:]) == 1):  # Check for arg
        port = sys.argv[1]
    m = mocoder(sport=port)
    m.decoding_loop()


if __name__ == '__main__':
    main()
