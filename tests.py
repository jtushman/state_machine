import functools
import os
import nose
from nose.plugins.skip import SkipTest
from nose.tools import *
from nose.tools import assert_raises

try:
    import mongoengine
except ImportError:
    mongoengine = None

def establish_mongo_connection():
    mongo_name = os.environ.get('AASM_MONGO_DB_NAME', 'test_acts_as_state_machine')
    mongo_port = int(os.environ.get('AASM_MONGO_DB_PORT', 27017))
    mongoengine.connect(mongo_name, port=mongo_port)

try:
    import sqlalchemy
    engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=False)
except ImportError:
    sqlalchemy = None



from state_machine import acts_as_state_machine, State, Event, InvalidStateTransition, StateMachine, MongoEngineStateMachine, SqlAlchemyStateMachine


def requires_mongoengine(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if mongoengine is None:
            raise SkipTest("mongoengine is not installed")
        return func(*args, **kw)

    return wrapper


def requires_sqlalchemy(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if sqlalchemy is None:
            raise SkipTest("sqlalchemy is not installed")
        return func(*args, **kw)

    return wrapper

###################################################################################
## Plain Old In Memory Tests
###################################################################################

def test_state_machine():
    @acts_as_state_machine
    class Robot():
        name = 'R2-D2'

        status = StateMachine(
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


    robot = Robot()
    eq_(robot.status, 'sleeping')
    assert robot.status.is_sleeping
    assert not robot.status.is_running
    robot.status.run()
    assert robot.status.is_running
    robot.status.sleep()
    assert robot.status.is_sleeping


def test_state_machine_no_callbacks():
    @acts_as_state_machine
    class Robot():
        name = 'R2-D2'

        status = StateMachine(
            sleeping=State(initial=True),
            running=State(),
            cleaning=State(),

            run=Event(from_states='sleeping', to_state='running'),
            cleanup=Event(from_states='running', to_state='cleaning'),
            sleep=Event(from_states=('running', 'cleaning'), to_state='sleeping')
        )

    robot = Robot()
    eq_(robot.status, 'sleeping')
    assert robot.status.is_sleeping
    assert not robot.status.is_running
    robot.status.run()
    assert robot.status.is_running
    robot.status.sleep()
    assert robot.status.is_sleeping


def test_multitple_machines_on_same_object():

    @acts_as_state_machine
    class Fish():

        activity = StateMachine(
            sleeping=State(initial=True),
            swimming=State(),

            swim=Event(from_states='sleeping', to_state='swimming'),
            sleep=Event(from_states='swimming', to_state='sleeping')
        )

        preparation = StateMachine(
            raw=State(inital=True),
            cooking=State(),
            cooked=State(),

            cook=Event(from_states='raw', to_state='cooking'),
            serve=Event(from_states='cooking', to_state='cooked'),
        )

        @activity.before('sleep')
        def do_one_thing(self):
            print("{} is sleepy".format(self.name))

        @activity.before('sleep')
        def do_another_thing(self):
            print("{} is REALLY sleepy".format(self.name))

        @activity.after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzz")

        @activity.after('sleep')
        def snore(self):
            print("Zzzzzzzzzzzzzzzzzzzzzz")

    fish = Fish()
    eq_(fish.activity, 'sleeping')
    assert fish.activity.is_sleeping
    assert not fish.activity.is_swimming
    fish.activity.swim()
    assert fish.activity.is_swimming
    fish.activity.sleep()
    assert fish.activity.is_sleeping

    # Question if there is not naming conflicts should we support shortcuts:
    # Such as:
    #
    # fish.is_swimming
    # fish.swim()
    #
    # vs.
    #
    # fish.activity.is_swimming
    # fish.activity.swim()


###################################################################################
## SqlAlchemy Tests
###################################################################################
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


###################################################################################
## Mongo Engine Tests
###################################################################################

@requires_mongoengine
def test_mongoengine_state_machine():

    @acts_as_state_machine
    class Person(mongoengine.Document):
        name = mongoengine.StringField(default='Billy')

        status = MongoEngineStateMachine(
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

    establish_mongo_connection()

    person = Person()

    person.save()
    eq_(person.status, 'sleeping')
    assert person.status.is_sleeping
    assert not person.status.is_running
    person.status.run()
    assert person.status.is_running
    person.status.sleep()
    assert person.status.is_sleeping
    person.status.run()
    person.save()

    person2 = Person.objects(id=person.id).first()
    assert person2.status.is_running


@requires_mongoengine
def test_invalid_state_transition():
    @acts_as_state_machine
    class Person(mongoengine.Document):
        name = mongoengine.StringField(default='Billy')

        status = MongoEngineStateMachine(
            sleeping=State(initial=True),
            running=State(),
            cleaning=State(),

            run=Event(from_states='sleeping', to_state='running'),
            cleanup=Event(from_states='running', to_state='cleaning'),
            sleep=Event(from_states=('running', 'cleaning'), to_state='sleeping')
        )

    establish_mongo_connection()
    person = Person()
    person.save()
    assert person.status.is_sleeping

    #should raise an invalid state exception
    with assert_raises(InvalidStateTransition):
        person.status.sleep()


@requires_mongoengine
def test_before_callback_blocking_transition():
    @acts_as_state_machine
    class Runner(mongoengine.Document):
        name = mongoengine.StringField(default='Billy')

        status = MongoEngineStateMachine(
            sleeping=State(initial=True),
            running=State(),
            cleaning=State(),

            run=Event(from_states='sleeping', to_state='running'),
            cleanup=Event(from_states='running', to_state='cleaning'),
            sleep=Event(from_states=('running', 'cleaning'), to_state='sleeping')
        )

        @status.before('run')
        def check_sneakers(self):
            return False

    establish_mongo_connection()
    runner = Runner()
    runner.save()
    assert runner.status.is_sleeping
    runner.status.run()
    runner.reload()
    assert runner.status.is_sleeping
    assert not runner.status.is_running


if __name__ == "__main__":
    nose.run()
