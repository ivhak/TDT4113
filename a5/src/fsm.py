'''
FSM
'''

from collections import namedtuple
from inspect import isfunction
from kpc import KPC
from led_board import LED
from keypad import Keypad


def any_symbol(*_):
    ''' Dummy function, returns True for all input '''
    return True


def valid_led(signal):
    '''
    Check that signal is a number between 1 and 6
    '''
    return 48 + 1 <= ord(signal) <= 48 + 6


def any_digit(signal):
    '''
    Check that signal is number between 1 and 6
    '''
    return 48 <= ord(signal) <= 48 + 9


def active(state):
    '''
    Returns wether or not state is active
    '''
    return state in ('S_ACTIVE', 'S_ACTIVE_2')


Rule = namedtuple('Rule', 'state1 state2 signal action')

RULES = [
    # State1        State2       Signal       Action
    ('S_INIT',     'S_READ',     any_symbol,  KPC.init_password_entry),    # INIT
    ('S_READ',     'S_READ',     any_digit,   KPC.append_next_digit),      # PW ADD DIGIT
    ('S_READ',     'S_VERIFY',   '*',         KPC.verify_pw),              # FINISH PW ENTRY
    ('S_READ',     'S_INIT',     any_symbol,  KPC.reset_agent),            # ABORT PW ENTRY
    ('S_VERIFY',   'S_ACTIVE',   'Y',         KPC.fully_activate),         # PW ACCEPTED
    ('S_VERIFY',   'S_INIT',     any_symbol,  KPC.reset_agent),            # PW NOT ACCEPTED
    (active,       'S_READ_2',   '*',         KPC.init_new_pass),          # BEGIN NEW PW ENTRY
    ('S_READ_2',   'S_READ_2',   any_digit,   KPC.append_next_digit),      # NEW PW ADD DIGIT 1
    ('S_READ_2',   'S_READ_3',   '*',         KPC.cache_pw_1),             # NEW PW FINISH ENTRY 1
    ('S_READ_2',   'S_ACTIVE',   any_symbol,  KPC.abort_new_pass),         # ABORT NEW PW
    ('S_READ_3',   'S_READ_3',   any_digit,   KPC.append_next_digit),      # NEW PW ADD DIGIT 2
    ('S_READ_3',   'S_ACTIVE',   '*',         KPC.reset_pw),               # FINISH NEW PW ENTRY
    ('S_READ_3',   'S_ACTIVE',   any_symbol,  KPC.abort_new_pass),         # ABORT NEW PW
    (active,       'S_LED',      valid_led,   KPC.select_led),             # SELECT LED
    ('S_LED',      'S_TIME',     '*',         KPC.reset_duration),         # BEGIN DURATION ENTRY
    ('S_TIME',     'S_TIME',     any_digit,   KPC.duration_next_digit),    # DURATION ADD DIGIT
    ('S_TIME',     'S_ACTIVE',   '*',         KPC.light_one_led),          # FINISH DURATION ENTRY
    ('S_ACTIVE',   'S_ACTIVE_2', '#',         KPC.logout_1),               # FIRST LOGOUT BTN PUSH
    ('S_ACTIVE_2', 'S_DONE',     '#',         KPC.logout_2),               # LOG OUT
    ('S_DONE',     'S_READ',     any_symbol,  KPC.init_password_entry),    # RESTART
]


class FSM:
    '''
    Finite State Machine.
    Perform an action based on the current state of the program and a signal,
    based on a set of rules.
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
        '''
        Check each of the rules, if none of them match reset the state to the
        default/start state.
        '''
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
        for rule_args in RULES:
            self.add_rule(Rule(*rule_args))

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
    ''' test FSM'''
    fsm = FSM()
    fsm.main_loop()


if __name__ == '__main__':
    main()
