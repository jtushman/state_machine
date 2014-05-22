import inspect

from state_machine.models import Event, State, StateMachine, InvalidStateTransition, MongoEngineStateMachine, SqlAlchemyStateMachine, AbstractStateMachine
# from state_machine.orm import get_adaptor

try:
    import mongoengine
except ImportError as e:
    mongoengine = None

# _temp_callback_cache = None
#
# def get_callback_cache():
#     global _temp_callback_cache
#     if _temp_callback_cache is None:
#         _temp_callback_cache = dict()
#     return _temp_callback_cache
#
# def get_function_name(frame):
#     return inspect.getouterframes(frame)[1][3]
#
# def before(before_what):
#     def wrapper(func):
#         frame = inspect.currentframe()
#         calling_class = get_function_name(frame)
#
#         calling_class_dict = get_callback_cache().setdefault(calling_class, {'before': {}, 'after': {}})
#         calling_class_dict['before'].setdefault(before_what, []).append(func)
#
#         return func
#
#     return wrapper
#
#
# def after(after_what):
#     def wrapper(func):
#
#         frame = inspect.currentframe()
#         calling_class = get_function_name(frame)
#
#         calling_class_dict = get_callback_cache().setdefault(calling_class, {'before': {}, 'after': {}})
#         calling_class_dict['after'].setdefault(after_what, []).append(func)
#
#         return func
#
#     return wrapper



# def _get_potential_state_machine_attributes(clazz):
#     if mongoengine is not None:
#         # reimplementing inspect.getmembers to swallow ConnectionError
#         results = []
#         for key in dir(clazz):
#             try:
#                 value = getattr(clazz, key)
#             except (AttributeError, mongoengine.ConnectionError):
#                 continue
#             results.append((key, value))
#         results.sort()
#         return results
#     else:
#         return inspect.getmembers(clazz)

# def acts_as_state_machine(original_class):
#
#     for member, value in _get_potential_state_machine_attributes(original_class):
#
#         if isinstance(value, AbstractStateMachine):
#             name, machine = member, value
#             setattr(machine, 'name', name)
#
#             # add extra_class memebers is necessary as such the case for mongo and sqlalchemy
#             for name in machine.extra_class_members:
#                 setattr(original_class, name, machine.extra_class_members[name])
#
#     return original_class

def acts_as_state_machine(original_class):

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

