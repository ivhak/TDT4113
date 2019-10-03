from RPi import GPIO


class Keypad:
    def __init__(self):
        pass

    def setup(self):
        GPIO.setmode(GPIO.BCM)

    def do_polling(self):
        return None

    def get_next_signal(self):
        signal = ''
        while signal is not None:
            signal = self.do_polling()
