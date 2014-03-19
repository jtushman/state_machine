from __future__ import absolute_import

try:
    import mongoengine
except ImportError:
    mongoengine = None

from state_machine.orm.base import BaseAdaptor


class MongoAdaptor(BaseAdaptor):
    def extra_class_members(self, initial_state):
        return {'aasm_state': mongoengine.StringField(default=initial_state.name)}

    def update(self, document, state_name):
        document.aasm_state = state_name


def get_mongo_adaptor(original_class):
    if mongoengine is not None and issubclass(original_class, mongoengine.Document):
        return MongoAdaptor(original_class)
    return None
