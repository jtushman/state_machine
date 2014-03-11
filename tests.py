import functools
import nose
from nose.plugins.skip import SkipTest
from nose.tools import *
from nose.tools import assert_raises

try:
    import mongoengine
    mongoengine.connect('test_acts_as_state_machine',port=37017)
except ImportError:
    mongoengine = None

from state_machine import acts_as_state_machine, before, State, Event, after, InvalidStateTransition

def requires_mongoengine(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if mongoengine is None:
            raise SkipTest("mongoengine is not installed")
        return func(*args, **kw)
    return wrapper


@requires_mongoengine
def test_state_machine():
    @acts_as_state_machine
    class Person(mongoengine.Document):
        name = mongoengine.StringField(default='Billy')

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

        @before('sleep')
        def do_one_thing(self):
            print "{} is sleepy".format(self.name)

        @before('sleep')
        def do_another_thing(self):
            print "{} is REALLY sleepy".format(self.name)

        @after('sleep')
        def snore(self):
            print "Zzzzzzzzzzzz"

        @after('sleep')
        def snore(self):
            print "Zzzzzzzzzzzzzzzzzzzzzz"


    person = Person()
    person.save()
    eq_(person.current_state,'sleeping')
    assert person.is_sleeping
    assert not person.is_running
    person.run()
    person.reload()
    assert person.is_running
    person.sleep()
    person.reload()
    assert person.is_sleeping


def test_multiple_machines():
    @acts_as_state_machine
    class Person(object):
        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

        @before('run')
        def on_run(self):
            things_done.append("Person.ran")

    @acts_as_state_machine
    class Dog(object):
        sleeping = State(initial=True)
        running = State()

        run = Event(from_states=sleeping, to_state=running)
        sleep = Event(from_states=(running,), to_state=sleeping)

        @before('run')
        def on_run(self):
            things_done.append("Dog.ran")


    things_done = []
    person = Person()
    dog = Dog()
    eq_(person.current_state,'sleeping')
    eq_(dog.current_state,'sleeping')
    assert person.is_sleeping
    assert dog.is_sleeping
    person.run()
    eq_(things_done, ["Person.ran"])


@requires_mongoengine
def test_invalid_state_transition():

    @acts_as_state_machine
    class Person(mongoengine.Document):
        name = mongoengine.StringField(default='Billy')

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

    person = Person()
    person.save()
    assert person.is_sleeping

    #should raise an invalid state exception
    with assert_raises(InvalidStateTransition):
        person.sleep()


@requires_mongoengine
def test_before_callback_blocking_transition():

    @acts_as_state_machine
    class Person(mongoengine.Document):
        name = mongoengine.StringField(default='Billy')

        sleeping = State(initial=True)
        running = State()
        cleaning = State()

        run = Event(from_states=sleeping, to_state=running)
        cleanup = Event(from_states=running, to_state=cleaning)
        sleep = Event(from_states=(running, cleaning), to_state=sleeping)

        @before('run')
        def check_sneakers(self):
            return False

    person = Person()
    person.save()
    assert person.is_sleeping
    person.run()
    person.reload()
    assert person.is_sleeping
    assert not person.is_running



if __name__ == "__main__":
    nose.run()