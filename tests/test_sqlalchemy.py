import functools

from nose.plugins.skip import SkipTest
from nose.tools import *
from nose.tools import assert_raises

try:
    import sqlalchemy
    engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=False)
except ImportError:
    sqlalchemy = None

from state_machine import acts_as_state_machine, State, Event, SqlAlchemyStateMachine
from state_machine import InvalidStateTransition, StateTransitionFailure

def requires_sqlalchemy(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if sqlalchemy is None:
            raise SkipTest("sqlalchemy is not installed")
        return func(*args, **kw)

    return wrapper

@requires_sqlalchemy
def test_sqlalchemy_state_machine():
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    Base = declarative_base()

    @acts_as_state_machine
    class Puppy(Base):
        __tablename__ = 'puppies'
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String)

        status = SqlAlchemyStateMachine(
            sleeping=State(initial=True),
            running=State(),
            cleaning=State(),

            run=Event(from_states='sleeping', to_state='running'),
            cleanup=Event(from_states='running', to_state='cleaning'),
            sleep=Event(from_states=('running', 'cleaning'), to_state='sleeping')
        )

        @status.before('sleep')
        def do_one_thing(self):
            print("{} is sleepy".format(self.name))

        @status.before('sleep')
        def do_another_thing(self):
            print("{} is REALLY sleepy".format(self.name))

        @status.after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzz")

        @status.after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzzzzzzzzzzzz")


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    puppy = Puppy(name='Ralph')

    eq_(puppy.status, 'sleeping')
    assert puppy.status.is_sleeping
    assert not puppy.status.is_running
    puppy.status.run()
    assert puppy.status.is_running

    session.add(puppy)
    session.commit()

    puppy2 = session.query(Puppy).filter_by(id=puppy.id)[0]

    assert puppy2.status.is_running


@requires_sqlalchemy
def test_sqlalchemy_state_machine_no_callbacks():
    ''' This is to make sure that the state change will still work even if no callbacks are registered.
    '''
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    Base = declarative_base()

    @acts_as_state_machine
    class Kitten(Base):
        __tablename__ = 'kittens'
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String)

        status = SqlAlchemyStateMachine(
            sleeping=State(initial=True),
            running=State(),
            cleaning=State(),

            run=Event(from_states='sleeping', to_state='running'),
            cleanup=Event(from_states='running', to_state='cleaning'),
            sleep=Event(from_states=('running', 'cleaning'), to_state='sleeping')
        )

        @status.before('sleep')
        def do_one_thing(self):
            print("{} is sleepy".format(self.name))

        @status.before('sleep')
        def do_another_thing(self):
            print("{} is REALLY sleepy".format(self.name))

        @status.after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzz")

        @status.after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzzzzzzzzzzzz")

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    kitten = Kitten(name='Kit-Kat')

    eq_(kitten.status, 'sleeping')
    assert kitten.status.is_sleeping
    assert not kitten.status.is_running
    kitten.status.run()
    assert kitten.status.is_running

    session.add(kitten)
    session.commit()

    kitten2 = session.query(Kitten).filter_by(id=kitten.id)[0]

    assert kitten2.status.is_running


@requires_sqlalchemy
def test_sqlalchemy_state_machine_using_initial_state():
    ''' This is to make sure that the database will save the object with the initial state.
    '''
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    Base = declarative_base()

    @acts_as_state_machine
    class Penguin(Base):
        __tablename__ = 'penguins'
        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        name = sqlalchemy.Column(sqlalchemy.String)

        status = SqlAlchemyStateMachine(
            sleeping=State(initial=True),
            running=State(),
            cleaning=State(),

            run=Event(from_states='sleeping', to_state='running'),
            cleanup=Event(from_states='running', to_state='cleaning'),
            sleep=Event(from_states=('running', 'cleaning'), to_state='sleeping')
        )

        @status.before('sleep')
        def do_one_thing(self):
            print("{} is sleepy".format(self.name))

        @status.before('sleep')
        def do_another_thing(self):
            print("{} is REALLY sleepy".format(self.name))

        @status.after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzz")

        @status.after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzzzzzzzzzzzz")


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Note: No state transition occurs between the initial state and when it's saved to the database.
    penguin = Penguin(name='Tux')
    eq_(penguin.status, 'sleeping')
    assert penguin.status.is_sleeping

    session.add(penguin)
    session.commit()

    penguin2 = session.query(Penguin).filter_by(id=penguin.id)[0]

    assert penguin2.status.is_sleeping


    #########################