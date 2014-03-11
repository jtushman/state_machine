import inspect
from functools import wraps

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

    class_name = original_class.__name__
    class_dict = {}
    adaptor = get_adaptor(original_class)

    global _temp_callback_cache

    class_dict['callback_cache'] = _temp_callback_cache

    def current_state_method():
        def f(self):
            return self.aasm_state
        return property(f)

    class_dict['current_state'] = current_state_method()

    class_dict.update(original_class.__dict__)

    # Get states
    initial_state = None
    members = get_user_attributes(original_class)
    is_method_dict = dict()
    for member,value in members:
        if isinstance(value, State):
            if value.initial:
                if initial_state is not None:
                    raise ValueError("multiple initial states!")
                initial_state = value

            #add its name to itself:
            setattr(value,'name',member)

            is_method_string = "is_" + member

            def is_method_builder(member):
                def f(self):
                    return self.aasm_state == str(member)
                return property(f)

            is_method_dict[is_method_string] = is_method_builder(member)

    class_dict.update(is_method_dict)
    class_dict.update(adaptor.extra_class_members(initial_state))

    # Get events
    members = get_user_attributes(original_class)
    event_method_dict = dict()
    for member,value in members:
        if isinstance(value, Event):
            # Create event methods

            def event_meta_method(event_name,event_description):
                def f(self):
                    #assert current state
                    if self.current_state not in event_description.from_states:
                        raise InvalidStateTransition

                    # fire before_change
                    failed = False
                    if event_name in self.__class__.callback_cache[class_name]['before']:
                        for callback in self.__class__.callback_cache[class_name]['before'][event_name]:
                            result = callback(self)
                            if result is False:
                                print "One of the 'before' callbacks returned false, breaking"
                                failed = True
                                break


                    #change state
                    if not failed:
                        adaptor.update(self, event_description.to_state.name)

                        #fire after_change
                        if event_name in self.__class__.callback_cache[class_name]['after']:
                            for callback in self.__class__.callback_cache[class_name]['after'][event_name]:
                                callback(self)

                return f
            event_method_dict[member] = event_meta_method(member,value)
    class_dict.update(event_method_dict)

    clazz = type(class_name, original_class.__bases__, class_dict)
    return clazz


class InvalidStateTransition(Exception):
    pass

class State(object):
    def __init__(self, initial=False, **kwargs):
        self.initial = initial

    def __eq__(self,other):
        if isinstance(other,basestring):
            return self.name == other
        elif isinstance(other,State):
            return self.name == other.name
        else:
            return False


    def __ne__(self,other):
        return not self == other

class Event(object):
    def __init__(self, **kwargs):
        self.to_state = kwargs.get('to_state',None)
        self.from_states = tuple()
        from_state_args = kwargs.get('from_states',tuple())
        if isinstance(from_state_args, (tuple,list)):
            self.from_states = tuple(from_state_args)
        else:
            self.from_states = (from_state_args,)



