from typing import Union

from convomeld.states import (
    ConvoStartState,
    ConvoStopState,
    ConvoAnswerState,
    ConvoQuestionState,
    ConvoInstructionState,
    ConvoIntroductionState,
)


def create_convo_start_state(
    worksheet_name: str, convo_description: str
) -> ConvoStartState:
    """Creates structure of the first block of convo which has 'start' state.
    Accepting already parsed worksheets and descriptions of microlessons.

    Args:
        sheet_names_sorted (list): Sequence of worksheets after sorting process
        microlesson_convo_descriptions (list): Sequence of microlessons descriptions

    Returns:
        list: Sequence of dict which has predefined structure of convo start block.
        I used list here because later I am smashing lists of different elements together including this one
    """

    name = "start"
    convo_name = f"{worksheet_name}"
    convo_description = f"{convo_description.lower()}"
    nlp = "case_insensitive"
    actions = {"en": [convo_description.capitalize()]}
    triggers = {
        "en": {
            "__next__": f"{worksheet_name}-introduction",
        }
    }

    return ConvoStartState(
        name=name,
        convo_name=convo_name,
        convo_description=convo_description,
        nlp=nlp,
        actions=actions,
        triggers=triggers,
    )


def create_convo_introduction_state(
    microlesson_introduction_data: list, worksheet_name: str
) -> ConvoIntroductionState:
    """Creates microlesspn-introduction structure for single microlesson

    Args:
        microlesson_introduction_data (list): Data from first row in microlesson worksheet
        worksheet_name (str): Name of worksheet

    Returns:
        Union[dict, None]: Dictionary of prefedined keys:values.
        If there is no welcome_message in microlesson worksheet than block is redundant
    """

    introduction_message = microlesson_introduction_data[1]

    name = f"{worksheet_name}-introduction"
    level = 0
    actions = {"en": [introduction_message.strip()]}
    triggers = {
        "en": {
            "__next__": f"{worksheet_name}-instruction",
        }
    }

    return ConvoIntroductionState(
        name=name,
        level=level,
        actions=actions,
        triggers=triggers,
    )


def create_convo_instruction_state(
    microlesson_instruction_data: list, worksheet_name: str
) -> ConvoInstructionState:
    """Creates microlesson-instruction  structure for single microlesson

    Args:
        microlesson_instruction_data (list): Data from first row in microlesson worksheet
        worksheet_name (str): Name of worksheet

    Returns:
        Union[dict, None]: Dictionary of prefedined keys:values.
        If there is no instruction message in microlesson worksheet than block is redundant
    """

    instruction_message = microlesson_instruction_data[3]

    name = f"{worksheet_name}-instruction"
    level = 0
    actions = {"en": [instruction_message]}
    buttons = {"en": {"OK": f"{worksheet_name}/q1"}}
    triggers = {
        "en": {
            str(
                microlesson_instruction_data[4]
            ).title(): f"{worksheet_name}/{microlesson_instruction_data[2].lower()}",
            "__default__": name,
        }
    }

    return ConvoInstructionState(
        name=name,
        level=level,
        actions=actions,
        buttons=buttons,
        triggers=triggers,
    )


def create_convo_question(
    question_raw_data: list, statenum: int, worksheet_name: str
) -> ConvoQuestionState:
    """Creates microlesson question worksheet_data structure

    Args:
      question_raw_data (list): Question data from microlesson worksheet
      statenum (int): Order number in sequence of questions
      worksheet_name (str): Name of microlesson's worksheet

    Returns:
      dict: Predefined keys:values for microlesson's single question worksheet_data
    """

    # Represent pictures with chosen format.Link should be on column #8
    actions_data = [question_raw_data[3]]
    if question_raw_data[7] and question_raw_data[7] != "-":
        question_image = f"[Image]({question_raw_data[7]})"
        actions_data.append(question_image)

    name = f"{worksheet_name}/q{statenum}"
    level = statenum
    actions = {"en": actions_data}
    buttons = {"en": {"OK": f"{worksheet_name}/q{statenum}"}}
    triggers = {
        "en": {
            str(question_raw_data[4])
            .title()
            .strip(): f"correct-answer-{worksheet_name}/q{statenum}",
            "__default__": f"wrong-answer-{worksheet_name}/q{statenum}",
        }
    }

    return ConvoQuestionState(
        name=name,
        level=level,
        actions=actions,
        buttons=buttons,
        triggers=triggers,
    )


def create_convo_wrong_answer_state(
    statenum: int, worksheet_name: str
) -> ConvoAnswerState:
    """Creates microlesson's question wrong answer structure

    Args:
        statenum (int): Order number in sequence of questions
        worksheet_name (str): Name of microlesson's worksheet

    Returns:
        dict: Predefined keys:values for microlesson's single question wrong answer
    """

    name = f"wrong-answer-{worksheet_name}/q{statenum}"
    actions = {"en": ["Oops! That's not correct. Let's try again."]}
    triggers = {"en": {"__next__": f"{worksheet_name}/q{statenum}"}}

    return ConvoAnswerState(
        name=name,
        actions=actions,
        triggers=triggers,
    )


def create_convo_correct_answer_state(
    statenum: int,
    worksheet_name: str,
    stop_state_next: Union[bool, None] = False,
) -> ConvoAnswerState:
    """Creates microlesson's question correct answer structure

    Args:
        statenum (int): Order number in sequence of questions
        worksheet_name (str): Name of microlesson's worksheet
        stop_state_next (Union[bool, None], optional): Defines end question of particular microlesson. Defaults to False.

    Returns:
        dict: Predefined keys:values for microlesson's single question correct answer
    """

    name = f"correct-answer-{worksheet_name}/q{statenum}"
    actions = {"en": ["Perfect!"]}
    triggers = {
        "en": {
            "__next__": f"{worksheet_name}/q{statenum + 1}"
            if not stop_state_next
            else f"stop"
        }
    }

    return ConvoAnswerState(
        name=name,
        actions=actions,
        triggers=triggers,
    )


def create_convo_stop_state(convo_name: str) -> ConvoStopState:
    triggers = {"en": {"__default__": "start"}}
    actions = {
        "en": [
            f"Congratulations, you have completed the {convo_name} micro-lesson."
            f"You can start over or choose another practice. Click 'Repeat' to complete {convo_name} "
            f"micro-lesson one more time"
        ]
    }

    return ConvoStopState(triggers=triggers, actions=actions)
