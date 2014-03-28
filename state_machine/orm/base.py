from __future__ import absolute_import
import inspect
from state_machine.models import Event, State, InvalidStateTransition


class BaseAdaptor(object):

    def __init__(self, original_class):
        self.original_class = original_class

    def get_potential_state_machine_attributes(self, clazz):
        return inspect.getmembers(clazz)

    def process_states(self, original_class):
        initial_state = None
        is_method_dict = dict()
        for member, value in self.get_potential_state_machine_attributes(original_class):

            if isinstance(value, State):
                if value.initial:
                    if initial_state is not None:
                        raise ValueError("multiple initial states!")
                    initial_state = value

                #add its name to itself:
                setattr(value, 'name', member)

                is_method_string = "is_" + member

                def is_method_builder(member):
                    def f(self):
                        return self.aasm_state == str(member)

                    return property(f)

                is_method_dict[is_method_string] = is_method_builder(member)

        return is_method_dict, initial_state

    def process_events(self, original_class):
        _adaptor = self
        event_method_dict = dict()
        for member, value in self.get_potential_state_machine_attributes(original_class):
            if isinstance(value, Event):
                # Create event methods

                def event_meta_method(event_name, event_description):
                    def f(self):
                        #assert current state
                        if self.current_state not in event_description.from_states:
                            raise InvalidStateTransition

                        # fire before_change
                        failed = False
                        if self.__class__.callback_cache and \
                                event_name in self.__class__.callback_cache[_adaptor.original_class.__name__]['before']:
                            for callback in self.__class__.callback_cache[_adaptor.original_class.__name__]['before'][event_name]:
                                result = callback(self)
                                if result is False:
                                    print("One of the 'before' callbacks returned false, breaking")
                                    failed = True
                                    break

                        #change state
                        if not failed:
                            _adaptor.update(self, event_description.to_state.name)

                            #fire after_change
                            if self.__class__.callback_cache and \
                                    event_name in self.__class__.callback_cache[_adaptor.original_class.__name__]['after']:
                                for callback in self.__class__.callback_cache[_adaptor.original_class.__name__]['after'][event_name]:
                                    callback(self)

                    return f

                event_method_dict[member] = event_meta_method(member, value)
        return event_method_dict

    def modifed_class(self, original_class, callback_cache):

        class_name = original_class.__name__
        class_dict = dict()

        class_dict['callback_cache'] = callback_cache

        def current_state_method():
            def f(self):
                return self.aasm_state
            return property(f)

        class_dict['current_state'] = current_state_method()

        class_dict.update(original_class.__dict__)

        # Get states
        state_method_dict, initial_state = self.process_states(original_class)
        class_dict.update(self.extra_class_members(initial_state))
        class_dict.update(state_method_dict)

        # Get events
        event_method_dict = self.process_events(original_class)
        class_dict.update(event_method_dict)

        clazz = type(class_name, original_class.__bases__, class_dict)
        return clazz

    def extra_class_members(self, initial_state):
        raise NotImplementedError

    def update(self, document, state_name):
        raise NotImplementedError
