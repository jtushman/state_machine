from __future__ import absolute_import
try:
    import sqlalchemy
    from sqlalchemy.orm import Session
except ImportError:
    sqlalchemy = None


class SqlAlchemyAdaptor(object):

    def __init__(self,original_class):
        self.original_class = original_class

    def extra_class_members(self, initial_state):
        return {'aasm_state': sqlalchemy.Column(sqlalchemy.String, default=initial_state.name)}

    def update(self,document,state_name):
        document.update(set__aasm_state=state_name)
        # how do we get a session in here ??
        session = None
        session.query(document.__class__).filter_by(self.id).update({"state": state_name})


def get_sqlalchemy_adaptor(original_class):
    if sqlalchemy is not None and issubclass(original_class, sqlalchemy.Base):
        return SqlAlchemyAdaptor
    return None
