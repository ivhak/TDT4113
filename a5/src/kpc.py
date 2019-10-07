'''
The keypad controller recieves signals from the keypad, and passes it on to the
finite state machine which evaluates what action the keypad controller should
perfom, for example tell the LED board to light an LED.
'''

import RPi.GPIO as GPIO

PASS_PATH = '/home/plab/projects/a5/pass.txt'


class KPC:
    ''' Keypad Controller '''
    def __init__(self):
        self.keypad = None
        self.led_board = None
        self.password = '000'
        self.password_buffer = None
        self.password_verified = False
        self.cache = ''
        self.led_num = 0
        self.led_dur = ''

    def read_pass(self):
        ''' Read in the password from the password file '''
        with open(PASS_PATH, 'r') as f_p:
            self.password = f_p.readline().rstrip('\n')

    def get_next_signal(self):
        '''
        Ask the keypad for the next signal, unless there was a password attempt
        that was successful, in that case just send 'Y'
        '''
        if self.password_verified:
            self.password_verified = False
            return 'Y'
        signal = self.keypad.get_next_signal()
        return signal

    def flash_leds(self):
        ''' Flash all LEDs on the LED board '''
        self.led_board.flash_all_leds(5)

    def twinkle_leds(self):
        ''' Twinkle all LEDs on the LED board '''
        self.led_board.twinkle_all_leds(5)

    ###################################
    #          RULE ACTIONS           #
    ###################################

    def exit_action(self, *_):
        ''' On exit, clean up '''
        GPIO.cleanup()

    def init_password_entry(self, *_):
        '''
        Start password entry by flashing leds and emptying password buffer
        '''
        self.led_board.startup_show()
        self.password_buffer = ''

    def verify_pw(self, *_):
        ''' Check if the password entry is the same as the pasword.  '''
        self.password_verified = self.password_buffer == self.password
        if self.password_verified:
            print('Password verified')
            self.led_board.twinkle_all_leds(2)
        else:
            self.led_board.flash_all_leds(2)
        self.password_buffer = ''

    def init_new_pass(self, *_):
        ''' Start new password entry '''
        self.password_buffer = ''
        print('Enter a new password:')

    def append_next_digit(self, digit):
        ''' Append a new digit to the password buffer '''
        self.password_buffer += digit
        print('Password buffer: {}'.format(self.password_buffer))

    def cache_pw(self, *_):
        ''' Cache first new password entry '''
        self.cache = self.password_buffer
        self.password_buffer = ''
        print('Enter password again')

    def reset_pw(self, *_):
        ''' Set new password, output it to the password file '''
        if self.cache == self.password_buffer:
            with open(PASS_PATH, 'w') as f_p:
                f_p.write(self.password_buffer)
            self.password = self.password_buffer
            print('Saved new password: {}'.format(self.password))
        else:
            print('Print password did not match.')

    def abort_new_pass(self, *_):
        ''' Abort new password entry ('#') '''
        print('Aborting new password entry')
        self.password_buffer = ''

    def fully_activate(self, *_):
        ''' Dummy function for when password is accepted '''
        print('Welcome!')

    def reset_agent(self, *_):
        ''' Go back to the inital state if password is wrong '''
        print('Wrong password')
        self.password_buffer = ''

    def select_led(self, led_num):
        ''' Select LED to light up '''
        print('Selected led: {}'.format(led_num))
        self.led_num = ord(led_num) - 49

    def reset_duration(self, *_):
        ''' Empty the duration '''
        print('Enter a duration')
        self.led_dur = ''

    def duration_next_digit(self, dur):
        ''' Append a digit to the duration '''
        self.led_dur += dur
        print('Current set duration: {}'.format(self.led_dur))

    def light_one_led(self, *_):
        ''' Light the led the user chose for the duration chosen '''
        self.led_board.light_led(self.led_num, dur=int(self.led_dur))

    def logout_1(self, *_):
        ''' First logout request '''
        print('Press once more to log out...')

    def logout_2(self, *_):
        ''' Second logout request, logout '''
        self.led_board.shutdown_show()
        print('Logging out')
