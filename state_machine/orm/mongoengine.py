from __future__ import absolute_import

try:
    import mongoengine
except ImportError as e:
    mongoengine = None

from state_machine.orm.base import BaseAdaptor


class MongoAdaptor(BaseAdaptor):

    def get_potential_state_machine_attributes(self, clazz):
        # reimplementing inspect.getmembers to swallow ConnectionError
        results = []
        for key in dir(clazz):
            try:
                value = getattr(clazz, key)
            except (AttributeError, mongoengine.MongoEngineConnectionError):
                continue
            results.append((key, value))
        results.sort()
        return results


    def extra_class_members(self, initial_state):
        return {'aasm_state': mongoengine.StringField(default=initial_state.name)}

    def update(self, document, state_name):
        document.aasm_state = state_name


def get_mongo_adaptor(original_class):
    if mongoengine is not None and issubclass(original_class, mongoengine.Document):
        return MongoAdaptor(original_class)
    return None
