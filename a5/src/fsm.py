from rule import Rule
from kpc import KPC


def any_key(_):
    return True


def valid_led(signal):
    return 48 + 1 <= ord(signal) <= 48 + 6


RULES = [
    ('?', '?', valid_led, KPC.light_one_led)            # Light led <signal>
    ('s0', 's1', any_key, KPC.start_password_entry)     # Enter password
]


class FSM:
    def __init__(self):
        self.rules = []
        self.state = None
        self.default_state = 0
        self.agent = None
        self.signal = None

    def add_rule(self, rule: Rule):
        self.rules.push(rule)

    def get_next_signal(self):
        self.signal = self.agent.get_next_signal()

    def run_rules(self):
        for rule in self.rules:
            if self.apply_rule(rule):
                self.fire_rule(rule)
                break

    def apply_rule(self, rule: Rule):
        return rule.match(self.state, self.signal)

    def fire_rule(self, rule: Rule):
        self.state = rule.state2
        rule.action(self.agent, self.signal)

    def main_loop(self):
        for rule in RULES:
            self.add_rule(*rule)

        while self.state != self.default_state:
            self.get_next_signal()
            self.run_rules()
