import nose
from nose.tools import *
from nose.tools import assert_raises
import mongoengine
from acts_as_state_machine import acts_as_state_machine, before, State, Event, after, InvalidStateTransition

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