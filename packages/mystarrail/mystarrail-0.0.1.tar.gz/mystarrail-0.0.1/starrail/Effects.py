class Effect:
    def __init__(self, ls, TYPE=None, NAME=None, user=None, stack_upbound = 1):
        self.TYPE = TYPE
        self.name = NAME
        self.ls = ls # [func or stat, value, turns, trigger or not, stack]
        self.label, self.value, self.turns, self.trigger, self.stack = ls
        self.user = user
        self.stack_upbound = stack_upbound

    def __iter__(self):
        yield self.label
        yield self.value
        yield self.turns
        yield self.trigger
        yield self.stack

    def __getitem__(self, key):
        if key in self.ls:
            return self.ls[key]
        else:
            raise KeyError(f"'{key}' not found in Effect")

    def __str__(self):
        return f'{self.label} {self.value} {self.turns} {self.trigger} {self.stack}'

    def __isub__(self, other):
        self.turns -= other
        return self