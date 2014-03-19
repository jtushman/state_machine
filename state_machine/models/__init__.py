try:
    string_type = basestring
except NameError:
    string_type = str

class InvalidStateTransition(Exception):
    pass


class State(object):
    def __init__(self, initial=False, **kwargs):
        self.initial = initial

    def __eq__(self,other):
        if isinstance(other, string_type):
            return self.name == other
        elif isinstance(other, State):
            return self.name == other.name
        else:
            return False


    def __ne__(self, other):
        return not self == other


class Event(object):
    def __init__(self, **kwargs):
        self.to_state = kwargs.get('to_state', None)
        self.from_states = tuple()
        from_state_args = kwargs.get('from_states', tuple())
        if isinstance(from_state_args, (tuple, list)):
            self.from_states = tuple(from_state_args)
        else:
            self.from_states = (from_state_args,)
