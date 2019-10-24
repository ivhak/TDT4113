import motors


class Behavior:

    def __init__(self, bbcon, sensobs, pri):
        self.bbcon = bbcon
        self.sensobs = sensobs
        self.motor_recommendations = []
        self.active_flag = False
        self.halt_request = None  # ??
        self.priority = pri
        self.match_degree = 0  # Regnes ut i fra
        self.weight = 0  # self.match_degree * pri

    def consider_deactivation(self):
        if self.active_flag:
            # sjekk om den burde bli satt til inactive
            self.active_flag = False

    def consider_activation(self):
        if not self.active_flag:
            # Sjekke om burde bli satt til aktiv
            self.active_flag = True

    def update(self):
        if self.active_flag:
            self.consider_deactivation()
        else:
            self.consider_activation()
        self.match_degree = self.sense_and_act()
        self.update_weight()

    def sense_and_act(self):
        match_deg = 9
        return match_deg

    def update_weight(self):
        self.weight = self.match_degree * self.priority


class WhiteFloor(Behavior):
    """Roboten skal holde seg innenfor de svarte strekene.
    Denne oppførelen har pri = 1"""

    """IR-sensor gir ut en array [0,..., 5], med verdier fra 0-2000. 
    0 er hvit, og 2000 er svart"""

    def __init__(self, bbcon, sensobs, motors, flag, pri=1):
        super().__init__()

    def sense_and_act(self):
        # Value er en array
        value = self.sensobs.value
        maks = 300
        index = -1
        for number in value:
            if number > maks:
                maks = number
                index = value[number]
        degree = maks / 2000  # 2000 skal den få veldig høy degree
        # Da vil vi at roboten skal rygge
        if index == 0:
            self.motor_recommendations = motors.right()
        elif index == 5:
            self.motor_recommendations = motors.left()
        elif index == -1:
            self.motor_recommendations = motors.forward()
        else:
            self.motor_recommendations = motors.backward()
        # Evt halt-req
        return degree

def main():
    behav = WhiteFloor()
    behav.sense_and_act()


main()
