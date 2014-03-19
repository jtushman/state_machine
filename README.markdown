# state_machine
state machine for humans

There are two types of developers in this world: those who love state machines and those who *will* eventually.

I fall in the first camp.  I think it is really important to have a declarative way to define the states of
an object. That's why I developed `state_machine`.


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
    def big_snore(self):
        print "Zzzzzzzzzzzzzzzzzzzzzz"

person = Person()
print person.current_state == Person.sleeping       # True
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

###Before / After Callback Decorators
You can add callback hooks that get executed before or after an event (see example above).

*Important:* if the _before_ event causes an exception or returns `False`, the state
will not change (transition is blocked) and the _after_ event will not be executed.

###Blocks invalid state transitions
An _InvalidStateTransition Exception_ will be thrown if you try to move into an invalid state.



## ORM support

We have basic support for [mongoengine](http://mongoengine.org/), and [sqlalchemy](http://www.sqlalchemy.org/).

### Mongoengine

Just have your object inherit from `mongoengine.Document` and state_machine will add a StringField for state.

*Note:* You must explicitly call #save to persist the document to the datastore.

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
    eq_(person.current_state, Person.sleeping)
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

All you need to do is have sqlalchemy manage your object. For example:

```python
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()
    @acts_as_state_machine
    class Puppy(Base):
       ...
```

##Issues / Roadmap:
* Allow multiple state_machines per object
* Be able to configure the state field

## Questions / Issues
Feel free to ping me on twitter: [@tushman](http://twitter.com/tushman) or add issues or PRs at [https://github.com/jtushman/state_machine](https://github.com/jtushman/state_machine)

## Thank you
to [aasm](https://github.com/aasm/aasm) and ruby's [state_machine](https://github.com/pluginaweek/state_machine) and all other state machines that I loved before

