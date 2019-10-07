'''
FSM
'''

from inspect import isfunction
from kpc import KPC
from led_board import LED
from keypad import Keypad
from rules import RULES


class FSM:
    '''
    Finite State Machine.
    Perform an action based on the current state of the program and a signal,
    based on the set of rules defined in rules.py
    '''

    def __init__(self):
        self.rules = []
        self.state = 'S_INIT'
        self.agent = None
        self.signal = None

    def add_rule(self, rule):
        ''' Add a rule '''
        self.rules.append(rule)

    def get_next_signal(self):
        ''' Recieve next signal from the agent '''
        self.signal = self.agent.get_next_signal()

    def run_rules(self):
        ''' Check each of the rules, fire the first match '''
        for rule in self.rules:
            if self.apply_rule(rule):
                self.fire_rule(rule)
                return
        self.state = None

    def apply_rule(self, rule):
        ''' Check if the rule matches '''
        match = True

        # Check signal first
        if isfunction(rule.signal):
            match &= rule.signal(self.signal)
        else:
            match &= self.signal == rule.signal

        # Then check if state matches
        if isfunction(rule.state1):
            match &= rule.state1(self.state)
        else:
            match &= self.state == rule.state1
        return match

    def fire_rule(self, rule):
        ''' Apply the action of the matching rule. '''
        self.state = rule.state2
        rule.action(self.agent, self.signal)

    def main_loop(self):
        '''
        Run the finite state machine. While the state is not the default
        state, get a signal and choose which action to perfom.
        '''
        for rule in RULES:
            self.add_rule(rule)

        self.agent = KPC()
        self.agent.read_pass()

        self.agent.led_board = LED()
        self.agent.led_board.setup()

        self.agent.keypad = Keypad()
        self.agent.keypad.setup()

        while self.state is not None:
            try:
                self.get_next_signal()
                self.run_rules()
            except KeyboardInterrupt:
                pass

        self.agent.exit_action()


def main():
    ''' Run the keypad program'''
    fsm = FSM()
    fsm.main_loop()


if __name__ == '__main__':
    main()
