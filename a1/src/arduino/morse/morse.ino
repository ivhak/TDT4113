#define DOT     1
#define DASH    2
#define MPAUSE  3
#define LPAUSE  4

#define T       300 /* ms */

/*
 * Signal   |  Dot  | Dash | SPause | MPause | LPause |
 * Duration | <1.5T | >2T  |   2T   |  4.5T  |   7T   |
 */

const int button_pin = 7;
int button_state;
int init_state;
int start_t;
int delta_t;

void setup()
{
  Serial.begin(9600);
  pinMode(button_pin, INPUT);
  init_state = digitalRead(button_pin);
}

void loop()
{
  /* 
   *  Record how long the button stays in the same state, delta_t,
   *  then handle what will happen based on the start state
   */
  start_t = millis();
  while (digitalRead(button_pin) == init_state)
    ;
  delta_t = millis() - start_t;
  handle(init_state, delta_t);

  /*  The while loop has stopped -> state has changed */
  init_state = !init_state;
}

void handle(int state, int delta_t) {
  if (state == HIGH) {
    if (delta_t >= 1.5*T) {
      Serial.print(DASH);
    }
    else {
      Serial.print(DOT);
    }
  /*  Check if state has been low longer than SPAUSE */
  } else if (delta_t > 2*T && state == LOW) {
    if (delta_t <= 4.5*T) {
      Serial.print(MPAUSE);
    } else {
      Serial.print(LPAUSE);
    }
  }
}

void start_of_mess() {
  Serial.print(DOT);
  Serial.print(DOT);
  Serial.print(DOT);    /* s */

  Serial.print(MPAUSE);

  Serial.print(DASH);   /* t */

  Serial.print(MPAUSE);

  Serial.print(DOT);
  Serial.print(DASH);   /* a */

  Serial.print(MPAUSE);

  Serial.print(DOT);
  Serial.print(DASH);
  Serial.print(DOT);    /* r */

  Serial.print(MPAUSE);

  Serial.print(DASH);   /* t */

  Serial.print(LPAUSE);
}
