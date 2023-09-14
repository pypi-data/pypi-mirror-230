from abc import ABC, abstractmethod
from typing import Union
from collections.abc import Sequence
from convomeld.state import Action


class ActionMatcher(ABC):
    @abstractmethod
    def _match(self, action1, action2) -> bool:
        pass

    def match(self, actions1, actions2) -> bool:
        if isinstance(actions1, Action):
            actions1 = [actions1]
        if isinstance(actions2, Action):
            actions2 = [actions2]

        if len(actions1) != len(actions2):
            return False

        for action1, action2 in zip(actions1, actions2):
            if not self._match(action1, action2):
                return False

        return True


class SimpleActionMatcher(ActionMatcher):
    def _match(self, action1, action2) -> bool:
        return action1.name == action2.name and action1.args == action2.args


class TriggerUserTextMatcher(ABC):
    @abstractmethod
    def match(self, trigger_user_text_1, trigger_user_text_2):
        pass


class SimpleTriggerUserTextMatcher(TriggerUserTextMatcher):
    def match(self, trigger_user_text_1, trigger_user_text_2):
        return str(trigger_user_text_1) == str(trigger_user_text_2)
