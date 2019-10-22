"""
BBCON. yoyoyoyo
Mikkel sier: Har jeg fått det til nå?
Giske: jeg klarte det!
"""
import motors


class BBCON:

    def __init__(self):
        self.behaviors = []
        self.active_behaviors = []
        self.sensobs = []
        self.motobs = []
        self.arbitrator = None

    def add_behavior(self, behavior):
        """append a newly-created behavior onto the behaviors list"""
        if behavior not in self.behaviors:
            self.behaviors.append(behavior)

    def add_sensob(self, sensob):
        """append a newly-created sensob onto the sensobs list"""
        if sensob not in self.sensobs:
            self.sensobs.append(sensob)

    def activate_behavior(self, behavior):
        """add an existing behavior onto the active-behaviors list."""
        if behavior in self.behaviors:
            self.active_behaviors.append(behavior)

    def deactivate_behavior(self, behavior):
        """Remove an existing behavior from the active behaviors list."""
        if behavior in self.active_behaviors:
            self.active_behaviors.remove(behavior)

    def run_one_timestep(self):
        for sensob in self.sensobs:
            sensob.update()

        for behav in self.behaviors:
            behav.update()

        for motor in self.motobs:
            motor.update()

    '''def choose_action(self):
        """choose a winning be-havior and return that
        behavior’s motor recommendations and halt request flag"""

        return self.arbitrator.choose_action() '''


class Sensobs:

    def __init__(self, sensors):
        self.sensors = sensors
        self.value = []

    def update(self):
        for sensor in self.sensors:
            newValue = sensor.get_value()
            self.value.append(newValue)

    def get_value(self):
        return self.value


class Motob:

    def __init__(self, motors):
        self.motors = motors
        self.value = []

    def update(self):
        self.motor[0].set_value(self.value[0])
        self.motor[1].set_value(self.value[1])

    def operationalize(self):
        pass

    def set_value(self, value):
        self.value = value


class Behavior:

    def __init__(self, bbcon, sensobs, pri):
        self.bbcon = bbcon
        self.sensobs = sensobs
        self.motor_recommendations = []
        self.active_flag = False
        self.halt_request = []  # ??
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
        self.weight = self.match_degree *self.priority


class WhiteFloor(Behavior):
    """Roboten skal holde seg innenfor de svarte strekene.
    Denne oppførelen har pri = 1"""

    """IR-sensor gir ut en array [0,..., 5], med verdier fra 0-2000. 
    0 er hvit, og 2000 er svart"""

    def __init__(self, bbcon, sensobs, motors, flag, pri=1):
        super().__init__()

    def sense_and_act(self):
        #Value er en array
        value = self.sensobs.value
        maks = 300
        index = -1
        for number in value:
            if number > maks:
                maks = number
                index = value[number]
        degree = maks/2000  # 2000 skal den få veldig høy degree
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


class Avoid(Behavior):
    """Roboten skal unngå hindringer.
    Denne oppførselen har pri = 2"""

    """Antar at høy verdi(600) er nærme"""

    def __init__(self, bbcon, sensobs, motors, flag, pri=2):
        super().__init__()

    def sense_and_act(self):
        value = self.sensobs.value
        degree = value/600  # Hvis vi antar 600 er veldig nært
        # Da vil vi at roboten skal rygge
        self.motor_recommendations = motors.backward()
        # Evt halt-req
        return degree


class FindRed(Behavior):
    """Roboten skal finne de røde tingene vi har plassert ut.
    Denne har pri = 3"""

    def __init__(self, bbcon, sensobs, motors, flag, pri=3):
        super().__init__()

    def sense_and_act(self):
        # Antar vi får inn en RGB = (R, G, B)
        value = self.sensobs.value
        red = value[0] - value[1] - value[2]
        degree = value/255  # 255 er veeeldig rød
        # Da vil vi at roboten skal rygge
        self.motor_recommendations = motors.forward() # Kan feks sette farten til maks sånn at vi kjører den røde gjenstanden ned
        # Evt halt-req
        return degree

class Arbitrator:

    def __init__(self):
        self.actions = []
        self.active

    def choose_action(self):
        return self.actions, self.active
