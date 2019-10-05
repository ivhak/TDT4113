'''
FSM
'''

from rule import Rule
from kpc import KPC


def any_dummy(_):
    ''' Dummy function '''
    return True


def valid_led(signal):
    '''
    Check that signal is a number between 1 and 6
    '''
    return 48 + 1 <= ord(signal) <= 48 + 6


RULES = [
    # state1    state2  signal     action
    (any_dummy, '?', valid_led, KPC.light_one_led)    # Light led
    ('s0', 's1', any_dummy, KPC.init_password_entry)  # Enter password
]


class FSM:
    '''
    Finite State Machine.
    Perform an action based on the current state of the program and a signal,
    based on a set of rules.
    '''

    def __init__(self):
        self.rules = []
        self.state = None
        self.default_state = 0
        self.agent = None
        self.signal = None

    def add_rule(self, rule: Rule):
        ''' Add a rule '''
        self.rules.append(rule)

    def get_next_signal(self):
        ''' Recieve next signal from the agent '''
        self.signal = self.agent.get_next_signal()

    def run_rules(self):
        '''
        Check each of the rules, if none of them match reset the state to the
        default/start state.
        '''
        for rule in self.rules:
            if self.apply_rule(rule):
                self.fire_rule(rule)
                return
        self.state = self.default_state

    def apply_rule(self, rule: Rule):
        ''' Check if the rule matches '''
        return rule.match(self.state, self.signal)

    def fire_rule(self, rule: Rule):
        ''' Apply the action of the matching rule. '''
        self.state = rule.state2
        rule.action(self.agent, self.signal)

    def main_loop(self):
        '''
        Run the finite state machine. While the state is not the default
        state, get a signal and choose which action to perfom.
        '''
        for rule in RULES:
            self.add_rule(*rule)

        while self.state != self.default_state:
            self.get_next_signal()
            self.run_rules()
