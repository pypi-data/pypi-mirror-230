class ToDictMixin:
    def to_dict(self):
        return self.__dict__


class ConvoStartState(ToDictMixin):
    """Conversation Start State."""

    def __init__(
        self,
        convo_name: str,
        convo_description: str,
        nlp: str,
        actions: dict[str, list[str]],
        triggers: dict[str, dict[str, str]],
        name: str = "start",
    ):
        self.name = name
        self.convo_name = convo_name
        self.convo_description = convo_description
        self.nlp = nlp
        self.actions = actions
        self.triggers = triggers


class ConvoStopState(ToDictMixin):
    """Conversation Stop State."""

    def __init__(
        self,
        actions: dict,
        triggers: dict[str, dict[str, str]],
        name: str = "stop",
    ):
        self.name = name
        self.actions = actions
        self.triggers = triggers


class ConvoIntroductionState(ToDictMixin):
    def __init__(
        self,
        name: str,
        level: int,
        actions: dict[str, dict[str, str]],
        triggers: dict[str, dict[str, str]],
    ):
        self.name = name
        self.level = level
        self.actions = actions
        self.triggers = triggers


class ConvoInstructionState(ToDictMixin):
    def __init__(
        self,
        name: str,
        level: int,
        actions: dict[str, dict[str, str]],
        buttons: dict[str, dict[str, str]],
        triggers: dict[str, dict[str, str]],
    ):
        self.name = name
        self.level = level
        self.actions = actions
        self.buttons = buttons
        self.triggers = triggers


class ConvoQuestionState(ToDictMixin):
    def __init__(
        self,
        name: str,
        actions: dict[str, list],
        level: int = 0,
        buttons: dict[str, dict[str, str]] = {},
        triggers: dict[str, dict[str, str]] = {},
    ):
        self.name = name
        self.level = level
        self.actions = actions
        if buttons:
            self.buttons = buttons
        if triggers:
            self.triggers = triggers


class ConvoAnswerState(ToDictMixin):
    def __init__(
        self,
        name: str,
        actions: dict[str, list[str]],
        triggers: dict[str, dict[str, str]],
    ):
        self.name = name
        self.actions = actions
        self.triggers = triggers


class ConvoGraph:
    def __init__(self, worksheet_name_source_data: str):
        self.__states = []
        self.__current_convo_name = worksheet_name_source_data

    def add_state(self, state):
        self.__states.append(state)

    def __add__(self, other_convo_graph):
        if not isinstance(other_convo_graph, ConvoGraph):
            raise ValueError("You can concatenate only ConvoGraph objects")

        def update_start_state():
            other_convo_start_state = other_convo_graph.__states[0]
            self.__states[0].convo_description += (
                "/" + other_convo_start_state.convo_description
            )
            self.__states[0].convo_name += "__" + other_convo_start_state.convo_name

        def update_stop_state():
            self.__states[-1].name = f"stop-{self.__current_convo_name}"

            # Handle function for state before StopState
            if "__next__" in self.__states[-2].triggers["en"]:
                self.__states[-2].triggers["en"]["__next__"] = self.__states[-1].name
            else:
                for key, value in self.__states[-2].triggers["en"].items():
                    if (
                        key not in ["__default__", "__next__"]
                        and self.__states[-2].triggers["en"][key] == "stop"
                    ):
                        self.__states[-2].triggers["en"][key] = self.__states[-1].name
            self.__states[-1].triggers["en"][
                "__default__"
            ] = f"{other_convo_graph.__states[0].convo_name}-introduction"

        def concatenate_states():
            # Exclude start state of other Convo
            states_copy = other_convo_graph.__states[1:]
            self.__states.extend(states_copy)

        update_start_state()
        update_stop_state()
        concatenate_states()

        self.__current_convo_name = other_convo_graph.__current_convo_name

        return self

    def to_list_of_dicts(self):
        return [state.to_dict() for state in self.__states]

    def populate_convo(self, data: list):
        for state in data:
            if "start" in state["name"]:
                self.__states.append(ConvoStartState(**state))
            elif "introduction" in state["name"]:
                self.__states.append(ConvoIntroductionState(**state))
            elif "instruction" in state["name"]:
                self.__states.append(ConvoInstructionState(**state))
            elif "answer" in state["name"]:
                self.__states.append(ConvoAnswerState(**state))
            elif "stop" in state["name"]:
                self.__states.append(ConvoStopState(**state))
            else:
                self.__states.append(ConvoQuestionState(**state))
