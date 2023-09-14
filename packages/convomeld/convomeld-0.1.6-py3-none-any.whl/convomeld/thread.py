from __future__ import annotations
from typing import Iterator, Optional, Union
from collections.abc import Iterator
from convomeld.state import Action, State, Trigger, TriggerPlaceholder
from uuid import uuid4


class ConvoThread:
    def __init__(self) -> None:
        self._states = {}
        self._uuid = uuid4().hex[-6:]
        self._first_state = None
        self._last_state = None
        self._state_count = 0

    def __repr__(self) -> str:
        return f"ConvoThread(states={repr(self._states)}, first_state_name={repr(self._first_state and self._first_state.name)})"

    def __str__(self) -> str:
        res = ""

        for state in self.iter_states():
            trigger_str = (
                f"--{state.triggers[0].user_text}-->"
                if len(state.triggers) == 1
                else ""
            )
            res += f"{str(state)} {trigger_str} "

        return res

    def iter_states(self, with_prev_trigger=False) -> ConvoThreadIterator:
        self.validate()
        return ConvoThreadIterator(
            self._states,
            self._first_state and self._first_state.name,
            with_prev_trigger=with_prev_trigger,
        )

    def copy(self):
        self.validate()
        copy = ConvoThread()

        for state, prev_trigger in self.iter_states(with_prev_trigger=True):
            if prev_trigger is None:
                tp = TriggerPlaceholder.empty()
            else:
                tp = TriggerPlaceholder.from_trigger(prev_trigger)

            copy = copy.append_state(state.actions, tp, **state.attrs)

        return copy

    # Utils section

    def num_states(self) -> int:
        self.validate()
        return len(self._states)

    def num_triggers(self) -> int:
        self.validate()
        return max(len(self._states) - 1, 0)

    def get_first_state(self) -> Optional[State]:
        self.validate()
        return self._first_state and self._first_state.copy()

    def get_last_state(self) -> Optional[State]:
        self.validate()
        return self._last_state and self._last_state.copy()

    def append_state(self, actions, tp, **state_attrs) -> ConvoThread:
        self.validate()
        if isinstance(actions, Action):
            actions = [actions]

        self._state_count += 1
        new_state = State(
            f"path_{self._uuid}/state_{self._state_count}", actions, **state_attrs
        )
        self._states[new_state.name] = new_state

        if len(self._states) == 1:
            self._first_state = new_state
            self._last_state = new_state
            self.validate()
            return self

        prev_trigger = tp.create_trigger(new_state.name)
        self._last_state.triggers.append(prev_trigger)
        self._last_state = new_state
        self.validate()
        return self

    def prepend_state(self, actions, tp, **state_attrs) -> ConvoThread:
        self.validate()
        if isinstance(actions, Action):
            actions = [actions]

        self._state_count += 1
        new_state = State(
            f"path_{self._uuid}/state_{self._state_count}", actions, **state_attrs
        )
        self._states[new_state.name] = new_state

        if len(self._states) == 1:
            self._first_state = new_state
            self._last_state = new_state
            self.validate()
            return self

        new_trigger = tp.create_trigger(self._first_state.name)
        new_state.triggers.append(new_trigger)
        self._first_state = new_state
        self.validate()
        return self

    def pop_first_state(self) -> Optional[State]:
        self.validate()

        if len(self._states) == 0:
            return None
        elif len(self._states) == 1:
            state = self._states.pop(self._first_state.name)
            self._first_state = None
            self._last_state = None
            return state.copy()
        else:
            state = self._states.pop(self._first_state.name)
            self._first_state = self._states[state.triggers[0].target]
            return state.copy()

    # Validation section

    def validate(self) -> None:
        self._validate_state_names()
        self._validate_linear()

    def _validate_state_names(self) -> None:
        for state_name, state in self._states.items():
            if state_name != state.name:
                raise RuntimeError("State names constraint of ConvoThread violated")

            for trigger in state.triggers:
                if trigger.target not in self._states:
                    raise RuntimeError("State names constraint of ConvoThread violated")

    def _validate_linear(self) -> None:
        if len(self._states) == 0:
            return

        current_state = self._first_state
        num_states = 0

        while current_state is not None and num_states <= len(self._states) + 1:
            if len(current_state.triggers) == 0:
                # Reached end
                current_state = None
            elif len(current_state.triggers) == 1:
                target = current_state.triggers[0].target
                current_state = self._states[target]
            else:
                raise RuntimeError("Linearity constraint of ConvoThread violated")

            num_states += 1

        if num_states != len(self._states):
            # print(self)
            raise RuntimeError("Linearity constraint of ConvoThread violated")


class ConvoThreadIterator(Iterator[Union[State, tuple[State, Trigger]]]):
    def __init__(self, states, first_state_name, with_prev_trigger) -> None:
        self._states = {
            state_name: state.copy() for state_name, state in states.items()
        }
        self._first_state = self._states.get(first_state_name, None)
        self._with_prev_trigger = with_prev_trigger

        self._current_state = self._first_state
        self._current_trigger = TriggerPlaceholder.none().create_trigger(
            self._current_state.name
        )

    def __next__(self) -> State:
        if self._current_state is None:
            raise StopIteration()

        current_state = self._current_state
        current_trigger = self._current_trigger

        if len(self._current_state.triggers) == 0:
            # Reached end
            next_state = None
            next_trigger = None
        else:
            next_trigger = self._current_state.triggers[0]
            next_state = self._states[next_trigger.target]

        # Prepare next iterator state
        self._current_state = next_state
        self._current_trigger = next_trigger

        # Collect result
        if self._with_prev_trigger:
            result = (current_state, current_trigger)
        else:
            result = current_state

        return result
