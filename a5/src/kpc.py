
class KPC:
    def __init__(self):
        self.keypad = None
        self.led_board = None
        self.password_path = None
        self.password_buffer = None

    def init_password_entry(self):
        self.password_buffer = None
        if self.keypad.get_next_signal() is not None:
            self.led_board.flash_leds()
            # skru på masse lys for å indikere at nå starter prosessen

    def get_next_signal(self):
        signal = self.keypad.get_next_signal()
        if signal is not None:
            self.password_buffer.push(signal)

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
