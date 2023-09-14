from __future__ import annotations


class Action:
    default_lang = "en"
    supported_v2 = ["send_message"]
    supported_v3 = ["send_message"]

    def __init__(self, name, args) -> None:
        self.name = name
        self.args = args

    def __repr__(self) -> str:
        return f"Action(name={repr(self.name)}, args={repr(self.args)})"

    def copy(self, name=None, args=None) -> Action:
        if name is None:
            name = self.name
        if args is None:
            args = self.args

        return Action(name, args)

    @classmethod
    def send_message(cls, text, lang=None):
        action_name = "send_message"
        action_args = {
            "bot_text": text,
            "lang": lang if lang is not None else cls.default_lang,
        }
        return cls(action_name, action_args)


class Trigger:
    type_default = "__default__"
    type_next = "__next__"
    type_timeout = "__timeout__"
    type_empty = ""
    type_none = None

    default_lang = "en"

    def __init__(self, user_text, target, lang) -> None:
        self.user_text = user_text
        self.target = target
        self.lang = lang

    def __repr__(self) -> str:
        return f"Trigger(user_text={repr(self.user_text)}, target={repr(self.target)}, lang={repr(self.lang)})"

    def copy(self, user_text=None, target=None, lang=None) -> Trigger:
        if user_text is None:
            user_text = self.user_text
        if target is None:
            target = self.target
        if lang is None:
            lang = self.lang

        return Trigger(user_text, target, lang)

    def is_default(self) -> bool:
        return self.user_text == Trigger.type_default

    def is_next(self) -> bool:
        return self.user_text == Trigger.type_next

    def is_none(self) -> bool:
        return self.user_text == Trigger.type_none

    def is_timeout(self) -> bool:
        return self.user_text == Trigger.type_timeout


class TriggerPlaceholder:
    def __init__(self, user_text, lang) -> None:
        self.user_text = user_text
        self.lang = lang

    def __repr__(self) -> str:
        return f"TriggerPlaceholder(user_text={repr(self.user_text)}, lang={repr(self.lang)})"

    def create_trigger(self, target):
        if self.user_text == Trigger.type_empty:
            raise RuntimeError(
                "Empty trigger placeholder cannot be used to instantiate trigger"
            )

        return Trigger(self.user_text, target, self.lang)

    @classmethod
    def empty(cls) -> TriggerPlaceholder:
        return cls(Trigger.type_empty, Trigger.default_lang)

    @classmethod
    def none(cls) -> TriggerPlaceholder:
        return cls(Trigger.type_none, Trigger.default_lang)

    @classmethod
    def default(cls) -> TriggerPlaceholder:
        return cls(Trigger.type_default, Trigger.default_lang)

    @classmethod
    def next(cls) -> TriggerPlaceholder:
        return cls(Trigger.type_next, Trigger.default_lang)

    @classmethod
    def timeout(cls) -> TriggerPlaceholder:
        return cls(Trigger.type_timeout, Trigger.default_lang)

    @classmethod
    def from_trigger(cls, trigger) -> TriggerPlaceholder:
        return cls(trigger.user_text, trigger.lang)


class State:
    def __init__(self, name, actions=None, triggers=None, **attrs) -> None:
        self.name = name
        self.attrs = attrs

        if actions is None:
            self.actions = []
        else:
            self.actions = [action.copy() for action in actions]

        if triggers is None:
            self.triggers = []
        else:
            self.triggers = [trigger.copy() for trigger in triggers]

    def __repr__(self) -> str:
        return f"State(name={repr(self.name)}, actions={repr(self.actions)}, triggers={repr(self.triggers)}, **{repr(self.attrs)})"

    def copy(self, name=None, actions=None, triggers=None, **attrs) -> State:
        if name is None:
            name = self.name
        if actions is None:
            actions = self.actions
        if triggers is None:
            triggers = self.triggers

        attrs = {**self.attrs, **attrs}

        new_state = State(name, **attrs)
        new_state.actions = [action.copy() for action in actions]
        new_state.triggers = [trigger.copy() for trigger in triggers]
        return new_state

    def find_trigger(
        self, trigger, matcher, index=False, ensure_unique_targets=True
    ) -> Optional[Union[Trigger, int]]:
        if isinstance(trigger, Trigger):
            user_text = trigger.user_text
            lang = trigger.lang
            target = trigger.target
        elif isinstance(trigger, TriggerPlaceholder):
            user_text = trigger.user_text
            lang = trigger.lang
            target = None

        for i, trigger in enumerate(self.triggers):
            if trigger.lang == lang and (
                trigger.user_text == user_text
                or matcher.match(trigger.user_text, user_text)
            ):
                if target is not None and trigger.target != target:
                    if ensure_unique_targets:
                        raise RuntimeError(
                            f'Inconsistent state name in state "{self.name}" for trigger {repr(target)} : {repr(trigger)}'
                        )
                    else:
                        continue

                if index:
                    return i
                else:
                    return trigger.copy()

        return None

    def remove_trigger(self, target, matcher) -> Optional[Trigger]:
        index = self.find_trigger(target, matcher, index=True)
        return self.triggers.pop(index).copy() if index is not None else None

    # Export section

    def to_dict(self, use_unique_triggers=True, version="v2") -> dict:
        if version in ("v2", 2):
            return self._to_dict_v2(use_unique_triggers)
        elif version in ("v3", 3):
            return self._to_dict_v3(use_unique_triggers)

        raise RuntimeError(f"Unsupported version: expected 'v2'/'v3', got {version}")

    def _to_dict_v2(self, use_unique_triggers):
        attrs = {k: v for k, v in self.attrs.items() if not k.startswith("_")}
        state_dict = {
            "name": self.name,
            **attrs,
        }

        if len(self.actions):
            state_dict["actions"] = actions_dict = {}

            for action in self.actions:
                if action.name not in Action.supported_v2:
                    continue

                actions_dict.setdefault(action.args["lang"], [])
                actions_dict[action.args["lang"]].append(action.args["bot_text"])

        if len(self.triggers):
            state_dict["triggers"] = triggers_dict = {}

            for trigger in self.triggers:
                triggers_dict.setdefault(trigger.lang, {})
                if use_unique_triggers:
                    triggers_dict[trigger.lang][trigger.user_text] = trigger.target
                else:
                    triggers_dict[trigger.lang].setdefault(trigger.user_text, [])
                    triggers_dict[trigger.lang][trigger.user_text].append(
                        trigger.target
                    )

        return state_dict

    def _to_dict_v3(self, use_unique_triggers):
        attrs = {k: v for k, v in self.attrs.items() if not k.startswith("_")}
        state_dict = {
            "name": self.name,
            **attrs,
        }

        if len(self.actions):
            state_dict["actions"] = actions_list = []

            for action in self.actions:
                if action.name not in Action.supported_v3:
                    continue

                action_dict = {action.name: action.args}
                actions_list.append(action_dict)

        if len(self.triggers):
            state_dict["triggers"] = triggers_list = []

            for trigger in self.triggers:
                trigger_dict = {
                    "user_text": trigger.user_text,
                    "target": trigger.target,
                    "lang": trigger.lang,
                }
                triggers_list.append(trigger_dict)

        return state_dict

    # Import section

    @classmethod
    def from_dict(cls, state_dict, version=None) -> State:
        if version in ("v2", 2):
            return cls._from_dict_v2(cls, state_dict)
        elif version in ("v3", 3):
            return cls._from_dict_v3(cls, state_dict)
        elif version is None:
            try:
                return cls._from_dict_v2(cls, state_dict)
            except AttributeError:
                pass
            try:
                return cls._from_dict_v3(cls, state_dict)
            except AttributeError:
                pass

        raise RuntimeError(f"Unsupported version: expected 'v2'/'v3', got {version}")

    def _from_dict_v2(cls, state_dict):
        state_dict = state_dict.copy()
        actions = state_dict.pop("actions", {})
        triggers = state_dict.pop("triggers", {})

        state = cls(name=state_dict.pop("name"), **state_dict)

        for action_lang, action_group in actions.items():
            for action_text in action_group:
                state.actions.append(Action.send_message(action_text, action_lang))

        for trigger_lang, trigger_group in triggers.items():
            for user_text, next_target in trigger_group.items():
                state.triggers.append(Trigger(user_text, next_target, trigger_lang))

        return state

    def _from_dict_v3(cls, state_dict):
        state_dict = state_dict.copy()
        actions = state_dict.pop("actions", [])
        triggers = state_dict.pop("triggers", [])

        state = cls(name=state_dict.pop("name"), **state_dict)

        for action_dict in actions:
            if len(action_dict) != 1:
                raise RuntimeError(
                    f"Unexpected action format for v3: expected dict of size 1, got {action_dict}"
                )

            action_dict = action_dict.copy()
            action_name, action_args = action_dict.popitem()
            action = Action(action_name, action_args)
            state.actions.append(action)

        for trigger_dict in triggers:
            user_text = trigger_dict["user_text"]
            target = trigger_dict["target"]
            lang = trigger_dict.get("lang", Trigger.default_lang)
            state.triggers.append(Trigger(user_text, target, lang))

        return state
