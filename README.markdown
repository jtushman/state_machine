# state_machine
state machine for humans

There are two types of developers in this world: those that love state machines, and those that will eventually love
state machines.

I fall in the first camp.  I think that is really important to have a very declarative way to define the states of
an object.  And it is with this in mind that I developed `state_machine`


## Install

```bash
pip install state_machine
```


## Basic Usage

```python

@acts_as_state_machine
class Person():
    name = 'Billy'

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
print person.current_state == person.sleeping       # True
print person.is_sleeping                            # True
print person.is_running                             # False
person.run()
print person.is_running                             # True
person.sleep()

# Billy is sleepy
# Billy is REALLY sleepy
# Zzzzzzzzzzzz
# Zzzzzzzzzzzzzzzzzzzzzz

print person.is_sleeping                            # True


```


## Features

* Before / After Callback Decorators
You can add callback hooks that get executed before or after an event.  As seen as the example above.

One important feature / thing to know is if any of the before events fires and exception or returns `False` the state
transition will be blocked.  Also the after events will not be fired

* Blocks invalid state transistions
An InvalidStateTransition Exception will be thrown if you try to move into an invalid state from your current state



## ORM support

We have also have basic support for mongoengine, and sqlalchemy

### Mongoengine

Just have your object inherit from `mongoengine.Document` and state_machine will add a StringField for state

Note:  You need to explictly need to call #save to persist the document to the datastore

```python
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
    eq_(person.current_state,Person.sleeping)
    assert person.is_sleeping
    assert not person.is_running
    person.run()
    assert person.is_running
    person.sleep()
    assert person.is_sleeping
    person.run()
    person.save()

    person2 = Person.objects(id=person.id).first()
    assert person2.is_running
```


### Sqlalchemy

Similarly we have support for sqlalchemy.  All you need to do is have your object be managed my sqlalchemy.
For example:

```python
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()
    @acts_as_state_machine
    class Puppy(Base):
       ...
```

### Known Issues / Roadmap:
* Allow multiple state_machines per object
* Be able to configure the field that state is set