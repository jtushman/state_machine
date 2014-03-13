import inspect
from functools import wraps

from state_machine.models import Event, State, InvalidStateTransition
from state_machine.orm import get_adaptor

def get_user_attributes(cls):
    boring = dir(type('dummy', (object,), {}))
    return [item
            for item in inspect.getmembers(cls)
            if item[0] not in boring]


_temp_callback_cache = None

def before(before_what):

    def wrapper(func):
        frame = inspect.currentframe()
        outer_frame = inspect.getouterframes(frame)
        frame,filename,line_number,function_name,lines,index = outer_frame[1]

        calling_class = function_name

        global _temp_callback_cache
        if _temp_callback_cache is None:
            _temp_callback_cache = dict()

        if calling_class not in _temp_callback_cache:
            _temp_callback_cache[calling_class] = {'before':{},'after':{}}

        if before_what not in _temp_callback_cache[calling_class]['before']:
            _temp_callback_cache[calling_class]['before'][before_what] = []

        _temp_callback_cache[calling_class]['before'][before_what].append(func)


        return func
    return wrapper


def after(after_what):
    def wrapper(func):

        frame = inspect.currentframe()
        outer_frame = inspect.getouterframes(frame)
        frame,filename,line_number,function_name,lines,index = outer_frame[1]
        calling_class = function_name

        global _temp_callback_cache
        if _temp_callback_cache is None:
            _temp_callback_cache = dict()

        if calling_class not in _temp_callback_cache:
            _temp_callback_cache[calling_class] = {'before':{},'after':{}}

        if after_what not in _temp_callback_cache[calling_class]['after']:
            _temp_callback_cache[calling_class]['after'][after_what] = []

        _temp_callback_cache[calling_class]['after'][after_what].append(func)

        return func
    return wrapper

def acts_as_state_machine(original_class):

    adaptor = get_adaptor(original_class)
    global _temp_callback_cache

    return adaptor.modifed_class(original_class, _temp_callback_cache)







