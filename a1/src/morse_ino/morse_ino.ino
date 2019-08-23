#define DOT     1
#define DASH    2
#define MPAUSE  3
#define LPAUSE  4

#define T       300 /* ms */

/*
 * Signal   | Dot | Dash | SPause | MPause | LPause |
 * Duration | <T  | >2T  |  1.5T  |  4.5T  |   7T   |
 */
 
const int button_pin = 7;
int button_state;
int state;
int start_t;
float delta_t;

void setup()
{
  Serial.begin(9600);
  pinMode(button_pin, INPUT);
  state = LOW;
}

void loop()
{
  /*
   * Get the state of the button at the beginning of the loop.
   * Record how long the button stays in the same state, delta_t, 
   * then handle what will happen based on the start state
   */
  state = digitalRead(button_pin);
  start_t = millis();
  while (digitalRead(button_pin) == state)
    ;
  delta_t = millis() - start_t;
  handle(state, delta_t);
}

void handle(int state, int delta_t) {
  if (state) {
    if (delta_t >= 2*T) {
      Serial.print(DASH);
    }
    else {
      Serial.print(DOT);
    }
  } else if (delta_t > 1*T && !state) { /* Check if state has been low longer than SPAUSE */
    if (delta_t <= 4.5*T) {
      Serial.print(MPAUSE);
    } else {
      Serial.print(LPAUSE);
    }
  }
}
