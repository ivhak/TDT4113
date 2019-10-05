import RPi.GPIO as GPIO


class Keypad:

    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns

    def setup(self):
        ''' Setup the keypad '''
        GPIO.SETMODE(GPIO.BCM)
        for row_p in self.rows:
            GPIO.setup(row_p, GPIO.OUT)
        for column_p in self.columns:
            GPIO.setup(column_p, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # Må legge inn delay her for å hindre støy
    def do_polling(self):
        ''' Poll all the keys '''
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
