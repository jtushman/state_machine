# state_machine
state machine for humans

## Install

```bash
pip install state_machine
```

Currently only for those folks who use mongoengine -- other support forthcoming


## Usage

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
    def big_snore(self):
        print "Zzzzzzzzzzzzzzzzzzzzzz"

person = Person()
person.save()
eq_(person.current_state,'sleeping')
assert person.is_sleeping
assert not person.is_running
person.run()
assert person.is_running
person.sleep()
# Billy is sleepy
# Billy is REALLY sleepy
# Zzzzzzzzzzzz
# Zzzzzzzzzzzzzzzzzzzzzz
assert person.is_sleeping


```
