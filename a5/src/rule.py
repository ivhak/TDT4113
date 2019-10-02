from inspect import isfunction


class Rule:
    __slots__ = ['state1', 'state2', 'signal', 'action']

    def __init__(self, state1, state2, signal, action):
        self.state1 = state1
        self.state2 = state2
        self.symbol = signal
        self.action = action

    def match(self, state, signal):

        # Check signal first
        if isfunction(self.symbol):
            if not self.symbol(signal):
                return False
        else:
            if self.symbol != signal:
                return False

        # Then check if state matches
        if isfunction(self.state1):
            return self.state1(state)
        return self.state1 == state
