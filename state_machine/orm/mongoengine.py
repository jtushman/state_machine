from __future__ import absolute_import
try:
    import mongoengine
except ImportError:
    mongoengine = None


class MongoAdaptor(object):

    def extra_class_member(self):
        return {'aasm_state': mongoengine.StringField(default='sleeping')}

    def update(self,document,state_name):
        document.update(set__aasm_state=state_name)


def get_mongo_adaptor(oringal_class):
    if mongoengine is not None and isinstance(original_class, Document):
        return MongoAdaptor()
    return None
