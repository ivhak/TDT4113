'''
Declaration for rules used by FSM
'''

from collections import namedtuple
from kpc import KPC


def any_symbol(*_):
    ''' Dummy function, returns True for all input '''
    return True


def valid_led(signal):
    ''' Check that signal is a number between 1 and 6 '''
    return 48 + 1 <= ord(signal) <= 48 + 6


def any_digit(signal):
    ''' Check that signal is number between 1 and 6 '''
    return 48 <= ord(signal) <= 48 + 9


def active(state):
    ''' Returns wether or not state is active '''
    return state in ('S_ACTIVE', 'S_ACTIVE_2')


Rule = namedtuple('Rule', 'state1 state2 signal action')

RULES = [
    # State1           State2        Signal       Action
    Rule('S_INIT',     'S_READ',     any_symbol,  KPC.init_password_entry),  # INIT
    Rule('S_READ',     'S_READ',     any_digit,   KPC.append_next_digit),    # PW ADD DIGIT
    Rule('S_READ',     'S_VERIFY',   '*',         KPC.verify_pw),            # FINISH PW ENTRY
    Rule('S_READ',     'S_INIT',     any_symbol,  KPC.reset_agent),          # ABORT PW ENTRY
    Rule('S_VERIFY',   'S_ACTIVE',   'Y',         KPC.fully_activate),       # PW ACCEPTED
    Rule('S_VERIFY',   'S_INIT',     any_symbol,  KPC.reset_agent),          # PW NOT ACCEPTED
    Rule(active,       'S_READ_2',   '*',         KPC.init_new_pass),        # BEGIN NEW PW ENTRY
    Rule('S_READ_2',   'S_READ_2',   any_digit,   KPC.append_next_digit),    # NEW PW ADD DIGIT 1
    Rule('S_READ_2',   'S_READ_3',   '*',         KPC.cache_pw),             # NEW PW FINISH ENTRY 1
    Rule('S_READ_2',   'S_ACTIVE',   any_symbol,  KPC.abort_new_pass),       # ABORT NEW PW
    Rule('S_READ_3',   'S_READ_3',   any_digit,   KPC.append_next_digit),    # NEW PW ADD DIGIT 2
    Rule('S_READ_3',   'S_ACTIVE',   '*',         KPC.reset_pw),             # FINISH NEW PW ENTRY
    Rule('S_READ_3',   'S_ACTIVE',   any_symbol,  KPC.abort_new_pass),       # ABORT NEW PW
    Rule(active,       'S_LED',      valid_led,   KPC.select_led),           # SELECT LED
    Rule('S_LED',      'S_TIME',     '*',         KPC.reset_duration),       # BEGIN DURATION ENTRY
    Rule('S_TIME',     'S_TIME',     any_digit,   KPC.duration_next_digit),  # DURATION ADD DIGIT
    Rule('S_TIME',     'S_ACTIVE',   '*',         KPC.light_one_led),        # FINISH DURATION ENTRY
    Rule('S_ACTIVE',   'S_ACTIVE_2', '#',         KPC.logout_1),             # FIRST LOGOUT BTN PUSH
    Rule('S_ACTIVE_2', 'S_DONE',     '#',         KPC.logout_2),             # LOG OUT
    Rule('S_DONE',     'S_READ',     any_symbol,  KPC.init_password_entry),  # RESTART
]
