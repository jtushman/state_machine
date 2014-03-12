from __future__ import absolute_import
import inspect
from state_machine.models import Event, State, InvalidStateTransition

class BaseAdaptor(object):

    def modifed_class(self, original_class, callback_cache):

        _adaptor = self

        class_name = original_class.__name__
        class_dict = {}

        class_dict['callback_cache'] = callback_cache

        def current_state_method():
            def f(self):
                return self.aasm_state
            return property(f)

        class_dict['current_state'] = current_state_method()

        class_dict.update(original_class.__dict__)

        # Get states
        initial_state = None
        is_method_dict = dict()
        for member,value in inspect.getmembers(original_class):
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
        class_dict.update(self.extra_class_members(initial_state))

        # Get events
        event_method_dict = dict()
        for member,value in inspect.getmembers(original_class):
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
                            _adaptor.update(self, event_description.to_state.name)

                            #fire after_change
                            if event_name in self.__class__.callback_cache[class_name]['after']:
                                for callback in self.__class__.callback_cache[class_name]['after'][event_name]:
                                    callback(self)

                    return f
                event_method_dict[member] = event_meta_method(member,value)
        class_dict.update(event_method_dict)

        clazz = type(class_name, original_class.__bases__, class_dict)
        return clazz

    def extra_class_members(self, initial_state):
        raise NotImplementedError

    def update(self,document,state_name):
        raise NotImplementedError