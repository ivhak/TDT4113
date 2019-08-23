#define DOT     1
#define DASH    2
#define MPAUSE  3
#define LPAUSE  4

#define T       300 /* ms */

/*
 * Signal   | Dot | Dash | SPause | MPause | LPause |
 * Duration | T   | 3T   |   T    |   3T   |   7T   |
 */
 
const int button_pin = 7;
int button_state;
int last_state = LOW;
int last_time;
int delta_t;

void setup()
{
    Serial.begin(9600);
    pinMode(button_pin, INPUT);
    last_time = millis();
}

void loop()
{
  button_state = digitalRead(button_pin);
  if (button_state == HIGH && last_state == LOW) {
    delta_t = millis() - last_time;
    if (delta_t >= T) {           /* Check if pause is longer than signal pause*/
      if (delta_t >= 7*T) {
        Serial.print(LPAUSE);     /* Word pause */
      }
      else if (delta_t >= 3*T) {  
        Serial.print(MPAUSE);     /* Letter pause */

      }
    }
    last_state = HIGH;
    last_time = millis();
  }
  if (button_state == LOW && last_state == HIGH) {
    last_state = LOW;
    delta_t = millis() - last_time;
    if (delta_t <= T) {
      Serial.print(DOT);
    }
    else if (delta_t <= 3*T) {
      Serial.print(DASH);
    }
  }
}
