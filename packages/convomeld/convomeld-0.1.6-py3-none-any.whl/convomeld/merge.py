from typing import Optional
from abc import ABC, abstractmethod
from convomeld.state import State, TriggerPlaceholder, Trigger
from convomeld.matchers import ActionMatcher, TriggerUserTextMatcher
from convomeld.thread import ConvoThread


class MergeHandler(ABC):
    @abstractmethod
    def merge(
        self, convograph, current_state, tp, next_subthread, merge_state
    ) -> Optional[State]:
        pass


class MergeValidator(MergeHandler):
    def __init__(self, trigger_matcher) -> None:
        super().__init__()
        self._trigger_matcher = trigger_matcher

    def merge(
        self, convograph, current_state, tp, next_subthread, merge_state
    ) -> Optional[State]:
        self.validate_base_state(current_state, convograph)

        if merge_state is not None:
            if merge_state.name == "start":
                raise RuntimeError(
                    f'Validation error: merge_state {merge_state} is not expected to be a "start" state'
                )

            self.validate_base_state(merge_state, convograph)

    def validate_base_state(self, basic_state, convograph) -> None:
        # "start" state
        if basic_state.name == "start":
            if len(basic_state.triggers) != 1:
                raise RuntimeError(
                    'Validation error: "start" state is expected to have only 1 __next__ or __timeout__ trigger'
                )

            trigger = basic_state.triggers[0]
            target = convograph.find_state(name=trigger.target)
            is_trigger_valid_next = trigger.is_next() and target.name != "stop"
            is_trigger_valid_timeout = (
                trigger.is_timeout()
                and target.name == "stop"
                and convograph.num_states() == 2
            )

            if not (is_trigger_valid_next or is_trigger_valid_timeout):
                raise RuntimeError(
                    'Validation error: "start" state is expected to have only 1 __next__ or __timeout__ trigger'
                )

        # "stop" state
        if basic_state.name == "stop":
            # if len(basic_state.triggers) != 0:
            #     raise RuntimeError('Validation error: "stop" state is expected to have 0 triggers')

            if len(basic_state.triggers) != 1:
                raise RuntimeError(
                    'Validation error: "stop" state is expected to have 1 __default__ trigger to "start" state'
                )

            trigger = basic_state.triggers[0]
            target = convograph.find_state(name=trigger.target)
            is_trigger_valid_default = trigger.is_default() and target.name == "start"

            if not is_trigger_valid_default:
                raise RuntimeError(
                    'Validation error: "stop" state is expected to have 1 __default__ trigger to "start" state'
                )

        # basic state
        for trigger in basic_state.triggers:
            target = convograph.find_state(name=trigger.target)

            if trigger.is_next() and basic_state.name != "start":
                raise RuntimeError(
                    f"Validation error: current_state {basic_state} is not supposed to have __next__ triggers"
                )
            if trigger.is_timeout() and target.name != "stop":
                raise RuntimeError(
                    f"Validation error: current_state {basic_state} has invalid __timeout__ trigger"
                )

            while (
                target.find_trigger(TriggerPlaceholder.next(), self._trigger_matcher)
                is not None
            ):
                if len(target.triggers) != 1:
                    raise RuntimeError(
                        f"Validation error: if state has __next__ trigger it can only be single"
                    )
                target = convograph.find_state(name=target.triggers[0].target)


class DefaultTriggerHandler(MergeHandler):
    def __init__(self, trigger_matcher) -> None:
        super().__init__()
        self._trigger_matcher = trigger_matcher

    def merge(
        self, convograph, current_state, tp, next_subthread, merge_state
    ) -> Optional[State]:
        if current_state.name == "start":
            return

        default_trigger = TriggerPlaceholder.default().create_trigger(
            current_state.name
        )

        if current_state.find_trigger(default_trigger, self._trigger_matcher) is None:
            current_state.triggers.append(default_trigger)


class SubthreadAppendHandler(MergeHandler):
    def __init__(self, trigger_matcher) -> None:
        super().__init__()
        self._trigger_matcher = trigger_matcher

    def merge(
        self, convograph, current_state, tp, next_subthread, merge_state
    ) -> Optional[State]:
        if merge_state is not None:
            return

        for state, prev_trigger in next_subthread.iter_states(with_prev_trigger=True):
            new_state = convograph.create_state(state)
            trigger = (
                tp.create_trigger(new_state.name)
                if prev_trigger.is_none()
                else TriggerPlaceholder.from_trigger(prev_trigger).create_trigger(
                    new_state.name
                )
            )

            if current_state.find_trigger(trigger, self._trigger_matcher) is None:
                current_state.triggers.append(trigger)

            current_state = new_state

        return current_state


class SubthreadMergeHandler(MergeHandler):
    def __init__(self, action_matcher, trigger_matcher) -> None:
        super().__init__()
        self._action_matcher = action_matcher
        self._trigger_matcher = trigger_matcher

    def merge(
        self, convograph, current_state, tp, next_subthread, merge_state
    ) -> Optional[State]:
        if merge_state is None:
            return

        best_merge_result = self._find_best_merge_result(
            convograph, current_state, tp, next_subthread, merge_state
        )
        merge_result = self._perform_merge_result(
            convograph, current_state, tp, next_subthread, best_merge_result
        )
        return merge_result

    def _find_best_merge_result(
        self, convograph, current_state, tp, next_subthread, merge_state
    ) -> dict[str, str]:
        best_merge_result = {next_subthread.get_last_state().name: merge_state.name}
        next_subthread_states = [
            state for state in next_subthread.iter_states() if len(state.triggers)
        ]

        for trigger in current_state.triggers:
            existing_subthread_states = []
            target = convograph.find_state(name=trigger.target)

            while target.find_trigger(TriggerPlaceholder.next(), self._trigger_matcher):
                existing_subthread_states.append(target)
                target = convograph.find_state(name=target.triggers[0].target)

            if target is not merge_state:
                continue

            merge_result = {next_subthread.get_last_state().name: target.name}

            for existing_state, state_to_merge in zip(
                reversed(existing_subthread_states), reversed(next_subthread_states)
            ):
                if self._action_matcher.match(
                    existing_state.actions, state_to_merge.actions
                ):
                    merge_result[state_to_merge.name] = existing_state.name
                else:
                    break

            if len(merge_result) > len(best_merge_result):
                best_merge_result = merge_result

        return best_merge_result

    def _perform_merge_result(
        self, convograph, current_state, tp, next_subthread, merge_result
    ) -> State:
        for state, prev_trigger in next_subthread.iter_states(with_prev_trigger=True):
            if state.name in merge_result:
                # "state" should be merged with existing state
                target_state = convograph.find_state(name=merge_result[state.name])
            else:
                # state should be copied as a next state
                target_state = convograph.create_state(state)

            new_trigger = (
                tp.create_trigger(target_state.name)
                if prev_trigger.is_none()
                else TriggerPlaceholder.from_trigger(prev_trigger).create_trigger(
                    target_state.name
                )
            )

            if current_state.find_trigger(new_trigger, self._trigger_matcher) is None:
                current_state.triggers.append(new_trigger)

            current_state = target_state

        return current_state


class StopEarlyHandler(MergeHandler):
    def __init__(self, trigger_matcher) -> None:
        super().__init__()
        self._trigger_matcher = trigger_matcher

    def merge(self, convograph, current_state, tp, next_subthread, merge_state) -> None:
        if merge_state is None:
            raise RuntimeError("Unexpected merge_state: expected not None")

        if current_state is merge_state:
            return

        human_stop_early_triggers = []
        bot_stop_early_triggers = []
        normal_trigger_present = False

        for trigger in current_state.triggers:
            target = convograph.find_state(name=trigger.target)

            if target.name == "stop":
                if trigger.is_timeout():
                    human_stop_early_triggers.append(trigger)
                else:
                    bot_stop_early_triggers.append(trigger)
                continue

            while (
                target.find_trigger(TriggerPlaceholder.next(), self._trigger_matcher)
                is not None
            ):
                target = convograph.find_state(name=target.triggers[0].target)

            if target is not current_state:
                normal_trigger_present = True

        if normal_trigger_present:
            stop_early_triggers_to_remove = (
                human_stop_early_triggers + bot_stop_early_triggers
            )
        elif len(bot_stop_early_triggers) > 0:
            stop_early_triggers_to_remove = human_stop_early_triggers
        else:
            stop_early_triggers_to_remove = []

        for trigger in stop_early_triggers_to_remove:
            current_state.triggers.remove(trigger)

        if len(human_stop_early_triggers) > 0 and merge_state.name != "stop":
            merge_state.triggers.append(human_stop_early_triggers[0].copy())
