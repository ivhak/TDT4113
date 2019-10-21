"""
BBCON. yoyoyoyo
Mikkel sier: Har jeg fått det til nå?
Giske: jeg klarte det!
"""


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

    def choose_action(self):
        """choose a winning be-havior and return that
        behavior’s motor recommendations and halt request flag"""

        return self.arbitrator.choose_action()



class Sensobs:

    def __init__(self):
        self.sensors = []
        self.value = ()

    def update(self):
        for sensor in self.sensors:
            self.sensors[sensor] = sensor
            # fetch verdier

    def get_value(self):
        return self.value


class Motob:

    def __init__(self):
        self.motors = []
        self.value = []

    def update(self):
        pass

    def operationalize(self):
        pass


class Motors:

    def __init__(self):
        self.vector = []

    def set_value(self, v):
        self.vector = v

    def stop(self):
        self.vector = [0, 0]


class Behavior:

    def __init__(self, bbcon, sensobs, motors, flag, pri, degree):
        self.bbcon = bbcon
        self.sensobs = sensobs
        self.motor_recommendations = motors
        self.active_flag = flag
        self.halt_request = []  # ??
        self.priority = pri
        self.match_degree = degree
        self.weight = degree * pri

    def consider_deactivation(self):
        if self.active_flag:
            #sjekk om den burde bli satt til inactive
            self.active_flag = False

    def consider_activation(self):
        if not self.active_flag:
            #Sjekke om burde bli satt til aktiv
            self.active_flag = True

    def update(self):
        pass

    def sense_and_act(self):
        pass


class Arbitrator:

    def __init__(self):
        self.actions = []
        self.active

    def choose_action(self):
        return self.actions, self.active

