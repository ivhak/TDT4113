#define DOT     1
#define DASH    2
#define MPAUSE  3
#define LPAUSE  4

#define T       400 /* ms */

/*
 * Signal   | Dot | Dash | SPause | MPause | LPause |
 * Duration | T   | 3T   |   T    |   3T   |   7T   |
 */
 
const int button_pin = 7;
int button_state;
int last_state = LOW;
int last_up;
int last_down;
int delta_t;

void setup()
{
    Serial.begin(9600);
    pinMode(button_pin, INPUT);
    last_up = millis();
    last_down = millis();
}

void loop()
{
  button_state = digitalRead(button_pin);
  if (button_state == HIGH && last_state == LOW) {
    delta_t = millis() - last_down; /* Time spent in LOW state */
    if (delta_t >= T) {             /* Check if pause is longer than signal pause*/
      if (delta_t <= 3*T) {
        Serial.print(MPAUSE);       /* Letter pause */
      }
      else if (delta_t <= 7*T) {  
        Serial.print(LPAUSE);       /* Word pause */

      }
    }
    last_state = HIGH;
    last_up = millis();
  }
  if (button_state == LOW && last_state == HIGH) {
    last_state = LOW;
    last_down = millis();
    delta_t = millis() - last_up;
    if (delta_t <= T) {
      Serial.print(DOT);
    }
    else if (delta_t <= 3*T) {
      Serial.print(DASH);
    }
  }
}

void test() {
  Serial.print(DOT);
  Serial.print(DOT);
  Serial.print(DOT);
  Serial.print(DOT);
  Serial.print(MPAUSE);
  Serial.print(DOT);
  Serial.print(MPAUSE);
  Serial.print(DOT);
  Serial.print(DOT);
  Serial.print(LPAUSE);
  Serial.print(DOT);
  Serial.print(DOT);
  Serial.print(DOT);
  Serial.print(DOT);
  Serial.print(MPAUSE);
  Serial.print(DOT);
  Serial.print(MPAUSE);
  Serial.print(DOT);
  Serial.print(DOT);
  Serial.print(LPAUSE);
}
