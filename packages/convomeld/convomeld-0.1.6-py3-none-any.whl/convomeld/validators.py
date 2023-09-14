import re


class ConvographValidationError(Exception):
    """Exception processing the Convograph grammar (syntax)

    We do not currently use the error_codes feature.

    From https://stackoverflow.com/a/1319675
    """

    error_codes = {}

    def __init__(self, message, error_codes={}):
        """error_codes can be used as shorthand for error messages"""
        super().__init__(message)
        self.error_codes.update(error_codes)


class ConvographValidator:
    def __init__(self, file_content):
        self.convograph = file_content

    def is_document_structure_valid(self):
        if not isinstance(self.convograph, list):
            return ConvographValidationError(
                f"A Convograph is a list of dictionaries and should have type `list` but yours is type {type(self.convograph)}. "
                "Perhaps you forgot to put leading '-' before one of your states in the YAML file."
            )
        for state in self.convograph:
            if not isinstance(state, dict):
                return ConvographValidationError(
                    f"The '{state}' state object is of type `{type(state)}` but should be `dict`. "
                    "Perhaps your state name doesn't have a leading '-' character or a trailing ':' character in the YAML file."
                )
        return True

    def are_states_fulfilled(self):
        for state in self.convograph:
            if "name" not in state:
                return ConvographValidationError(
                    f'"{state}" state doesn\'t have "name" keyword.'
                )
            for key in ("actions", "triggers"):
                if key not in state:
                    return ConvographValidationError(
                        f'"{state["name"]}" state doesn\'t have "{key}" keyword.'
                    )
        return True

    def are_names_valid(self):
        for s in self.convograph:
            if not self.is_name_valid(s["name"]):
                return ConvographValidationError(
                    f'"{s["name"]}" isn\'t valid name for state. It should contain alphanumerical, "_" or "/" characters.'
                )
        return True

    @staticmethod
    def is_name_valid(state_name):
        """State names must be lowercase alphanumeric and be valid python module paths.
        They must contain no whitespace or punctuation except "/" and "_".

        >>> ConvographValidator.is_name_valid('Hello')
        False
        >>> ConvographValidator.is_name_valid('hello_earth/from_mars')
        True
        """
        return bool(re.match("[a-z0-9_/]+", state_name))

    def is_start_state_exist(self):
        for state in self.convograph:
            if state["name"] == "start":
                return True
        return ConvographValidationError('No "start" state was found.')

    def is_start_state_valid(self):
        for state in self.convograph:
            if state["name"] == "start":
                if "convo_name" not in state:
                    return ConvographValidationError(
                        '"start" state doesn\'t have "convo_name" attribute.'
                    )
                if not self.is_name_valid(state["convo_name"]):
                    return ConvographValidationError(
                        f'"{state["convo_name"]}" isn\'t valid convo_name for state. It should contain alphanumerical, "_" or "/" symbols.'
                    )
                if "convo_description" not in state:
                    return ConvographValidationError(
                        '"start" state doesn\'t have "convo_description" attribute.'
                    )
                if not self.is_name_valid(state["convo_description"]):
                    return ConvographValidationError(
                        f'"{state["convo_description"]}" isn\'t valid convo_description for state. It should contain alphanumerical, "_" or "/" symbols.'
                    )
        return True

    def are_names_unique(self):
        state_names = []
        for state in self.convograph:
            state_names.append(state["name"])
        for s in state_names:
            if state_names.count(s) > 1:
                return ConvographValidationError(f'"{s}" state occurs more than once.')
        return True

    def are_actions_valid(self):
        for state in self.convograph:
            if not isinstance(state["actions"], dict):
                return ConvographValidationError(
                    f'"{state}" state has wrong value specified for "actions". It should be a dict type.'
                )
            for lang_a, v in state["actions"].items():
                if not isinstance(v, list):
                    return ConvographValidationError(
                        f'"{state}" state has wrong value specified for "{lang_a}" actions. It should be a list type.'
                    )
                if not len(v):
                    return ConvographValidationError(
                        f'"{lang_a}" actions are empty for "{state}" state.'
                    )
        return True

    def are_triggers_valid(self):
        for state in self.convograph:
            if not isinstance(state["triggers"], dict):
                return ConvographValidationError(
                    f'"{state}" state has wrong value specified for "tiggers". It should be a dict type.'
                )
            for lang_t, v in state["triggers"].items():
                if not isinstance(v, dict):
                    return ConvographValidationError(
                        f'"{state}" state has wrong value specified for "{lang_t}" triggers. It should be a dict type.'
                    )
                if not len(v):
                    return ConvographValidationError(
                        f'"{lang_t}" triggers are empty for "{state}" state.'
                    )
        return True

    def do_all_triggers_have_essential(self):
        for state in self.convograph:
            for lang_triggers in state["triggers"].values():
                if not all(
                    (
                        isinstance(self.is_dunder_trigger_valid(t, "__default__"), bool)
                        or isinstance(self.is_dunder_trigger_valid(t, "__next__"), bool)
                        for t in lang_triggers
                    )
                ):
                    return ConvographValidationError(
                        f'Neither "__default__ " nor "__next__" trigger was found for "{state}" state. Please, check spell.'
                    )
        return True

    @staticmethod
    def is_dunder_trigger_valid(trigger, mandatory_trigger):
        return trigger.strip().strip("_").strip().lower() == mandatory_trigger.strip(
            "__"
        )

    def are_target_states_exist(self):
        pointed_states = []
        target_states = []
        for state in self.convograph:
            target_states.append(state["name"])
            for lang_triggers in state["triggers"].values():
                for target_state in lang_triggers.values():
                    pointed_states.append(target_state)

        pointed_states = tuple(set(pointed_states))
        target_states = tuple(set(target_states))
        for s in pointed_states:
            if s not in target_states:
                return ConvographValidationError(f'"{s}" state doesn\'t exist!')
        return True

    def are_key_lengths_allowed(self):
        for state in self.convograph:
            for lang_a, v in state["actions"].items():
                if not all((len(a) <= 1024 for a in v)):
                    return ConvographValidationError(
                        f'Some of "{lang_a}" actions inside "{state}" state exceeded max length of 1024 characters.'
                    )
            for lang_t, v in state["triggers"].items():
                if not all((len(t) <= 1024 for t in v)):
                    return ConvographValidationError(
                        f'Some of "{lang_t}" triggers inside "{state}" state exceeded max length of 1024 characters.'
                    )
        return True

    def is_valid(self, convograph=None):
        if convograph is not None:
            self.convograph = convograph

        checks_to_pass = [
            self.is_document_structure_valid,
            self.are_states_fulfilled,
            self.are_names_valid,
            self.is_start_state_exist,
            self.is_start_state_valid,
            self.are_names_unique,
            self.are_actions_valid,
            self.are_triggers_valid,
            self.do_all_triggers_have_essential,
            self.are_target_states_exist,
            self.are_key_lengths_allowed,
        ]
        for check in checks_to_pass:
            invoked_check = check()
            if not isinstance(invoked_check, bool):
                raise invoked_check
        return True
