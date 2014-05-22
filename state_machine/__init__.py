import inspect

from state_machine.models import Event, State, StateMachine, InvalidStateTransition, MongoEngineStateMachine, SqlAlchemyStateMachine, AbstractStateMachine
# from state_machine.orm import get_adaptor

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


def acts_as_state_machine(original_class):
    """ Decorates classes that contain StateMachines to update the classes constructors and underlying
        structure if needed.

        For example for mongoengine it will add the necessary fields needed,
        and for sqlalchemy it updates the constructure to set the default states
    """

    if mongoengine and issubclass(original_class, mongoengine.Document):
        return _modified_class_for_mongoengine(original_class)
    elif sqlalchemy is not None and hasattr(original_class, '_sa_class_manager') and isinstance(
            original_class._sa_class_manager, instrumentation.ClassManager):
        return _modified_class_for_sqlalchemy(original_class)
    else:
        return modified_class(original_class)


def modified_class(original_class):
    for member, value in inspect.getmembers(original_class):

        if isinstance(value, AbstractStateMachine):
            name, machine = member, value
            setattr(machine, 'name', name)

            # add extra_class memebers is necessary as such the case for mongo and sqlalchemy
            for name in machine.extra_class_members:
                setattr(original_class, name, machine.extra_class_members[name])
    return original_class


def _modified_class_for_mongoengine(original_class):
    class_name = original_class.__name__
    class_dict = dict()
    class_dict.update(original_class.__dict__)
    extra_members = {}
    for member in class_dict:
        value = class_dict[member]

        if isinstance(value, AbstractStateMachine):
            name, machine = member, value
            setattr(machine, 'name', name)

            # add extra_class memebers is necessary as such the case for mongo and sqlalchemy
            for name in machine.extra_class_members:
                extra_members[name] = machine.extra_class_members[name]

    class_dict.update(extra_members)
    clazz = type(class_name, original_class.__bases__, class_dict)
    return clazz


def _modified_class_for_sqlalchemy(original_class):
    mod_class = modified_class(original_class)

    orig_init = mod_class.__init__

    def new_init_builder():
        def new_init(self, *args, **kwargs):
            orig_init(self, *args, **kwargs)

            for member, value in inspect.getmembers(mod_class):

                if isinstance(value, AbstractStateMachine):
                    machine = value
                    setattr(self, machine.underlying_name, machine.initial_state.name)

        return new_init

    mod_class.__init__ = new_init_builder()
    return mod_class







