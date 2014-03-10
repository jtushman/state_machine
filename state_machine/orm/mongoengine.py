from __future__ import absolute_import
import mongoengine

def extra_class_member():
    return {'aasm_state': mongoengine.StringField(default='sleeping')}


def update(document,state_name):
    document.update(set__aasm_state=state_name)
    