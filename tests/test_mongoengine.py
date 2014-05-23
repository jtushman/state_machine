import functools
import os
from nose.plugins.skip import SkipTest
from nose.tools import *
from nose.tools import assert_raises

try:
    import mongoengine
except ImportError:
    mongoengine = None

from state_machine import acts_as_state_machine, State, Event, MongoEngineStateMachine
from state_machine import InvalidStateTransition, StateTransitionFailure

def establish_mongo_connection():
    mongo_name = os.environ.get('AASM_MONGO_DB_NAME', 'test_acts_as_state_machine')
    mongo_port = int(os.environ.get('AASM_MONGO_DB_PORT', 27017))
    mongoengine.connect(mongo_name, port=mongo_port)


def requires_mongoengine(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if mongoengine is None:
            raise SkipTest("mongoengine is not installed")
        return func(*args, **kw)

    return wrapper


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