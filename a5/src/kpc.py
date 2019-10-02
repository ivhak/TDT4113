
class KPC:
    def __init__(self):
        self.keypad = None
        self.led_board = None
        self.password_path = None

    def init_passcorde_entry(self):
        pass

    def get_next_signal(self):
        pass

    def verify_login(self):
        pass

    def validate_passcode_change(self):
        pass

    def light_one_led(self, led_num):
        self.led_board.light_one_led(led_num)

    def flash_leds(self):
        self.led_board.flash_leds()

    def twinkle_leds(self):
        self.led_board.twinkle_all_leds()

    def exit_action(self):
        pass
