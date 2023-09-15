"""
A quick and dirty state machine inspired by a `Django Snippet`__\ , which was in
turn inspired by the rails plugin ``acts_as_state_machine``.

__ https://djangosnippets.org/snippets/737/

Changes that are made for this project were again inspired by the `transitions`__
module and the project's specific needs.

__ https://github.com/pytransitions/transitions

This FSM (Finite State Machine) can be applied to any *model* that has a finite
number of clearly defined states and transitions between those states.

First define the states that the model can be in and initialize a Machine object
with those states and an initial states.

Then you need to define the way that the model moves from one state to the next,
i.e. a *transition*. Add those transitions to the Machine object with the
``add_transition`` method.

The model will be adapted with methods that represent the transitions and methods
to query the state. The example below shows a simple model with two states\ [*]_\ , i.e.
'on' and 'off'::

    Class MyButton(QPushButton):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            states = ('on', 'off')

            self.machine = Machine(self, states, initial='on')

            self.machine.add_transition(trigger='set_on',  source='off', dest='on')
            self.machine.add_transition(trigger='set_off', source='on',  dest='off')

This will dynamically create two new methods in the class ``MyButton``, i.e. the
method ``set_on()`` and the method ``set_off()``. Additionally, there will be
two state checking method: ``is_on()`` and ``is_off()``. You can also check the
state of the model MyButton by inspecting the state attribute.

.. [*] When working in **Qt 5**, a similar state machine can better be implemented
       with the ``QStateMachine`` provided by the Qt framework. Check out this
       `example for a Two-way Button`__.

__ https://doc.qt.io/qt-5/qtwidgets-statemachine-twowaybutton-example.html

"""
import inspect
import logging

module_logger = logging.getLogger(__name__)


# You can't trivially replace this with `functools.partial` because this binds
# to classes and returns bound instances, whereas functools.partial (on
# CPython) is a type and its instances don't bind.
# source: from django.utils.functional import curry
def curry(_curried_func, *args, **kwargs):
    def _curried(*moreargs, **morekwargs):
        return _curried_func(*args, *moreargs, **{**kwargs, **morekwargs})

    return _curried


class MachineError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Machine():
    """
    Create a Finite State Machine (FSM).
    """

    def __init__(self, model, states, **kwargs):
        """
        Initialise the finite state machine.

        :param str model: the model object that needs to be converted into a FSM
        :param list states: a list with the names of the states
        :param str initial: the initial state
        """
        self.model = model
        self.state = None
        self.last_state = None

        try:
            initial_state = kwargs.pop('initial')
        except KeyError:
            raise MachineError("A Finite State Machine needs an initial state, "
                               "please provide the 'initial' keyword argument")

        module_logger.debug(f"Initial State = {initial_state}")

        self._set_initial(initial_state)

        self.states = []
        self.state_triggers = {}
        for state in states:
            if isinstance(state, str):
                self.states.append(state)
            elif isinstance(state, dict):
                state_name = list(state.keys())[0]
                self.states.append(state_name)
                self.state_triggers[state_name] = state[state_name]
        self.states = tuple(self.states)

    def _extract_from_state(self, kwargs):
        try:
            coming_from = kwargs.pop('from')
        except KeyError:
            raise MachineError("Missing 'from'; must transtion from a state")

        if isinstance(coming_from, str):
            if coming_from not in self.states and coming_from != '*':
                raise MachineError(f"from: '{coming_from}' is not a registered state")
        elif isinstance(coming_from, list):
            for state in coming_from:
                if state not in self.states:
                    raise MachineError(f"from: '{coming_from}' is not a registered state")

        return coming_from

    def _extract_to_state(self, kwargs):
        try:
            going_to = kwargs.pop('to')
        except KeyError:
            raise MachineError("Missing 'to'; must transition to a state")

        if going_to not in self.states and going_to != '<':
            raise MachineError(f"to: '{going_to}' is not a registered state")

        return going_to

    def _extract_run_method(self, kwargs):
        run = kwargs.pop('run', None)
        return run

    def _set_initial(self, initial):
        self._update_model(initial)

    def _update_state_from_model(self):
        self._update_state(self.model.state)

    def _update_model(self, state):
        self.model.state = state
        self._update_state(self.model.state)

    def _update_state(self, new_state):
        self.last_state = self.state if self.state is not None else new_state
        self.state = new_state

    def action(self, *args, **kwargs):
        name = kwargs.pop('this')
        module_logger.debug(f"Performing action: {name}, current state = {self.state}, last state = {self.last_state}")

        state = kwargs.pop('to_state')
        if state == '<':
            state = self.last_state

        run_method = kwargs.pop('run')

        self._update_state_from_model()

        from_states = kwargs.pop('from_states')
        from_states = from_states if from_states != "*" else [self.state]

        response = None

        if self.state in from_states:
            if state in self.state_triggers and 'enter' in self.state_triggers[state]:
                self.state_triggers[state]['enter']()
            if run_method is not None:
                response = run_method(*args, **kwargs)
            self._update_model(state)
            if state in self.state_triggers and 'leave' in self.state_triggers[state]:
                self.state_triggers[state]['leave']()
            return response
        else:
            module_logger.warning(f"Cannot transition from '{self.state}' to '{state}', nothing changed.")

        return response

    def is_state(self, state, *args):
        self._update_state_from_model()
        return self.state == state

    def get_state(self):
        self._update_state_from_model()
        return self.state

    def add_transition(self, trigger, source, dest, run=None):
        """
        Add a transition to the finite state machine.

        :param str trigger: the name of the trigger method (an action)
        :param str source: the name of the source state, from where the transition starts
        :param str dest: the name of the destination state, where the transition moves to
        :param function run: a function or method reference that will be called during the transition
        """
        if hasattr(self.model, trigger):
            module_logger.warning(
                f"Cannot overwrite attribute '{trigger}' in '{self.model.__class__.__name__}', no changes made.")
        else:
            setattr(self.model, trigger, curry(self.action, to_state=dest, from_states=source, this=trigger, run=run))
            module_logger.debug(f"Added method {trigger}() to {self.model.__class__.__name__}")

        if dest != '<':
            is_state = f"is_{dest}"

            if hasattr(self.model, is_state):
                module_logger.warning(
                    f"Attribute '{is_state}' already exists in '{self.model.__class__.__name__}', no changes made.")
            else:
                setattr(self.model, is_state, curry(self.is_state, dest))
                module_logger.debug(f"Added method {is_state}() to {self.model.__class__.__name__}")


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)


    class Button(object):
        pass


    class MyButton(Button):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            states = (
                'on',
                'off',
                {'disabled': {'enter': self.upon_entry, 'leave': self.upon_leave}},
                'hidden'
            )

            self.machine = Machine(self, states, initial='on')

            self.machine.add_transition(trigger='set_on', source='off', dest='on')
            self.machine.add_transition(trigger='set_off', source='on', dest='off')
            self.machine.add_transition(trigger='disable', source=['on', 'off'], dest='disabled')
            self.machine.add_transition(trigger='enable', source='disabled', dest='<')
            self.machine.add_transition(trigger='hide', source='*', dest='hidden', run=self.hide_)
            self.machine.add_transition(trigger='unhide', source='hidden', dest='<')

        def upon_entry(self):
            module_logger.debug(f"Entring: state = {self.state}")

        def upon_leave(self):
            module_logger.debug(f"Leaving: state = {self.state}")

        def hide_(self, *args, **kwargs):
            module_logger.debug(f"Running the {inspect.currentframe().f_code.co_name}() method...")
            module_logger.debug(f"args = {args}")
            module_logger.debug(f"kwargs = {kwargs}")


    b = MyButton()
    module_logger.debug(f"b.state={b.state}")

    actions = [b.set_off, b.hide, b.unhide, b.disable, b.enable, b.set_on, b.set_off]
    for action in actions:
        action()
        module_logger.debug(f"b.state={b.state}")

    b.hide("Hello, World!", type="string")
