import inspect

from state_machine.models import Event, State, InvalidStateTransition
from state_machine.orm import get_adaptor

_temp_callback_cache = None

def get_callback_cache():
    global _temp_callback_cache
    if _temp_callback_cache is None:
        _temp_callback_cache = dict()
    return _temp_callback_cache

def get_function_name(frame):
    return inspect.getouterframes(frame)[1][3]

def before(before_what):
    def wrapper(func):
        frame = inspect.currentframe()
        calling_class = get_function_name(frame)

        calling_class_dict = get_callback_cache().setdefault(calling_class, {'before': {}, 'after': {}})
        calling_class_dict['before'].setdefault(before_what, []).append(func)

        return func

    return wrapper


def after(after_what):
    def wrapper(func):

        frame = inspect.currentframe()
        calling_class = get_function_name(frame)

        calling_class_dict = get_callback_cache().setdefault(calling_class, {'before': {}, 'after': {}})
        calling_class_dict['after'].setdefault(after_what, []).append(func)

        return func

    return wrapper


def acts_as_state_machine(original_class):
    adaptor = get_adaptor(original_class)
    global _temp_callback_cache
    modified_class = adaptor.modifed_class(original_class, _temp_callback_cache)
    _temp_callback_cache = None
    return modified_class
