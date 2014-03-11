from __future__ import absolute_import
try:
    import mongoengine
except ImportError:
    mongoengine = None


class MongoAdaptor(object):

    def __init__(self,original_class):
        pass

    def extra_class_members(self):
        return {'aasm_state': mongoengine.StringField(default='sleeping')}

    def update(self,document,state_name):
        document.update(set__aasm_state=state_name)


def get_mongo_adaptor(original_class):
    if mongoengine is not None and issubclass(original_class, mongoengine.Document):
        return MongoAdaptor
    return None
