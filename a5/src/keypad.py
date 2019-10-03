import RPi.GPIO as GPIO

class keypad: 
  
  def __init__(self, rows, columns):
    self.rows = rows 
    self.columns = columns
    
 def setup(self):
     GPIO.SETMODE(GPIO.BCM)
     for rp in self.rows:
         GPIO.setup(rp, GPIO.OUT)
     for cp in self.columns:
         GPIO.setup(cp, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
 #Må legge inn delay her for å hindre støy
 def do_polling(self):
     for rp in self.rows:
         GPIO.output(rp, GPIO.HIGH)
         for cp in self.columns: 
             GPIO.input(cp) == GPIO.HIGH
             return [rp, cp]
         GPIO.output(rp, GPIO.LOW)
     return None
 
 def get_next_signal(self):
     do_polling = self.do_polling()
     while do_polling == None:
           do_polling = self.do_polling()
     # Gi beskjed til agent om at knapp er trykket ned
    return do_polling
