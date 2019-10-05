'''
Rule
'''
from inspect import isfunction


class Rule:
    '''
    Wrapper for the rules used in the finite state machine.
    '''
    __slots__ = ['state1', 'state2', 'signal', 'action']

    def __init__(self, state1, state2, signal, action):
        self.state1 = state1
        self.state2 = state2
        self.signal = signal
        self.action = action

    def match(self, state, signal):
        '''
        Check if state and signal fulfill the rule.
        '''

        # Check signal first
        if isfunction(self.signal):
            if not self.signal(signal):
                return False
        else:
            if self.signal != signal:
                return False

        # Then check if state matches
        if isfunction(self.state1):
            return self.state1(state)
        return self.state1 == state
