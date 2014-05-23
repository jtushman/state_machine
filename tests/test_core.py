
from nose.tools import *
from nose.tools import assert_raises

from state_machine import acts_as_state_machine, State, Event, StateMachine
from state_machine import InvalidStateTransition, StateTransitionFailure

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


def test_state_machine_event_wrappers():
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


        # This if sucessful will move from running or cleaning to sleeping
        # will raise invalid state if not a valid transition
        @status.on('run')
        def run(self):
            print("I'm running")

        @status.on('sleep')
        def sleep(self):
            print("I'm going back to sleep")


    robot = Robot()
    eq_(robot.status, 'sleeping')
    assert robot.status.is_sleeping
    assert not robot.status.is_running
    robot.run()
    assert robot.status.is_running
    robot.sleep()
    assert robot.status.is_sleeping



def test_state_machine_event_wrappers_block():
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


        # This if sucessful will move from running or cleaning to sleeping
        # will raise invalid state if not a valid transition
        @status.on('run')
        def try_running(self):
            print "I'm running"
            return False

        @status.on('sleep')
        def sleep(self):
            print "I'm going back to sleep"


    robot = Robot()
    eq_(robot.status, 'sleeping')
    assert robot.status.is_sleeping
    assert not robot.status.is_running

    #should raise an invalid state exception
    with assert_raises(StateTransitionFailure):
        robot.try_running()

    assert robot.status.is_sleeping