try:
    string_type = basestring
except NameError:
    string_type = str

try:
    import mongoengine
except ImportError as e:
    mongoengine = None

try:
    import sqlalchemy
    from sqlalchemy import inspection
    from sqlalchemy.orm import instrumentation
    from sqlalchemy.orm import Session
except ImportError:
    sqlalchemy = None
    instrumentation = None



class InvalidStateTransition(Exception):
    pass


class State(object):
    def __init__(self, initial=False, **kwargs):
        self.initial = initial

    def __eq__(self, other):
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
        self.name = None
        self.to_state = kwargs['to_state']
        self.from_states = tuple()
        from_state_args = kwargs.get('from_states', tuple())
        if isinstance(from_state_args, (tuple, list)):
            self.from_states = tuple(from_state_args)
        else:
            self.from_states = (from_state_args,)

        if self.to_state is None:
            raise TypeError("Expected to_state to be set")

        if self.from_states is None or len(self.from_states) == 0:
            raise TypeError("Expected From States to be set")

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.name == other
        elif isinstance(other, Event):
            return self.name == other.name


class AbstractStateMachine(object):
    """ Collection of states and events
    """

    def add_event(self, value):
        self.events[value.name] = value

    def add_state(self, state):
        self.states[state.name] = state

        # set initial value
        if state.initial:
            if self.initial_state is not None:
                raise ValueError("multiple initial states!")
            self.initial_state = state

    # add helper method is_<state.name>
    # for example is the state is sleeping
    # add a method is_sleeping()
    def __getattr__(self, item):
        if item.startswith('is_'):
            state_name = item[3:]
            return self.current_state == state_name
        elif item in self.events:
            return lambda: self.attempt_transition(self.events[item])
        else:
            raise AttributeError(item)


    def attempt_transition(self, event):
        if self.current_state not in event.from_states:
            raise InvalidStateTransition

        # fire before_change events
        failed = False

        # TODO: what do we need to overwrite so we can do:
        # event in ??
        if event.name in self.before_callbacks:
            for callback in self.before_callbacks[event.name]:
                result = callback(self)
                if result is False:
                    print("One of the 'before' callbacks returned false, breaking")
                    failed = True
                    break

        if not failed:
            self.update(event.to_state)

            # fire after change events
            if event.name in self.after_callbacks:
                for callback in self.after_callbacks[event.name]:
                    callback(self)


    @property
    def current_state(self):
        return getattr(self.parent, self.underlying_name)

    def __init__(self, **kwargs):
        self.events = self.states = {}
        self.initial_state = None

        self.before_callbacks = {}
        self.after_callbacks = {}
        self.underlying_name = None


        # parent refers to the object that this attribute is associted with so ...
        #     class Fish():
        #
        # activity = StateMachine(
        #     sleeping=State(initial=True),
        #     swimming=State(),
        #
        #    swim=Event(from_states='sleeping', to_state='swimming'),
        #    sleep=Event(from_states='swimming', to_state='sleeping')
        # )
        #
        # parent will refer to the instance of Fish
        self.parent = None

        for key in kwargs:
            value = kwargs[key]
            setattr(value, 'name', key)
            if isinstance(value, Event):
                self.add_event(value)
            elif isinstance(value, State):
                self.add_state(value)
            else:
                raise TypeError("Expecting Events and States, nothing else")



    # Descriptor Goodness
    # https://docs.python.org/2/howto/descriptor.html
    def __get__(self, instance, owner):
        if instance is not None:
            self.parent = instance
        return self

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.underlying_name = "sm_{}".format(value)


    @property
    def extra_class_members(self):
        raise NotImplementedError

    def update(self, new_state_name):
        raise NotImplementedError

    def before(self, before_what):
        def wrapper(func):
            self.before_callbacks.setdefault(before_what, []).append(func)
            return func
        return wrapper

    def after(self, after_what):
        def wrapper(func):
            self.after_callbacks.setdefault(after_what, []).append(func)
            return func
        return wrapper

    def __eq__(self, other):
        if isinstance(other, basestring):
            return self.current_state == other
        elif isinstance(other, State):
            return self.current_state == other.current_state


class StateMachine(AbstractStateMachine):

    @property
    def extra_class_members(self):
        return {self.underlying_name: self.initial_state}

    def update(self, state_name):
        setattr(self.parent, self.underlying_name, state_name)


class MongoEngineStateMachine(AbstractStateMachine):

    @property
    def extra_class_members(self):
        return {self.underlying_name: mongoengine.StringField(default=self.initial_state.name)}

    def update(self, state_name):
        setattr(self.parent, self.underlying_name, state_name)


class SqlAlchemyStateMachine(AbstractStateMachine):

    @property
    def extra_class_members(self):
        return {self.underlying_name: sqlalchemy.Column(sqlalchemy.String)}

    def update(self, state_name):
        setattr(self.parent, self.underlying_name, state_name)
