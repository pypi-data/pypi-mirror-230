from pandas import DataFrame

from convomeld.xlsx_csv_parsers import ConvoDataParser
from convomeld.states import ConvoGraph
from convomeld.data_factory import (
    create_convo_stop_state,
    create_convo_start_state,
    create_convo_question,
    create_convo_instruction_state,
    create_convo_introduction_state,
    create_convo_correct_answer_state,
    create_convo_wrong_answer_state,
)


def create_convograph(df: DataFrame, worksheet_name: str) -> ConvoGraph:
    data_from_df = df.values.tolist()
    convo_graph = ConvoGraph(worksheet_name_source_data=worksheet_name)
    convo_graph.add_state(
        create_convo_start_state(
            worksheet_name=worksheet_name,
            convo_description=f"A lesson about {data_from_df[0][0].lower()}",
        )
    )

    microlesson_welcome_data: list[str] = data_from_df[0]
    convo_graph.add_state(
        create_convo_introduction_state(
            microlesson_welcome_data, worksheet_name=worksheet_name
        )
    )
    convo_graph.add_state(
        create_convo_instruction_state(
            microlesson_welcome_data, worksheet_name=worksheet_name
        )
    )

    for statenum, question_state in enumerate(data_from_df[1:], 1):
        convo_graph.add_state(
            create_convo_question(
                question_raw_data=question_state,
                statenum=statenum,
                worksheet_name=worksheet_name,
            )
        )
        convo_graph.add_state(
            create_convo_wrong_answer_state(
                statenum=statenum, worksheet_name=worksheet_name
            )
        )
        if statenum == len(data_from_df) - 1:
            convo_graph.add_state(
                create_convo_correct_answer_state(
                    statenum=statenum,
                    worksheet_name=worksheet_name,
                    stop_state_next=True,
                )
            )
        else:
            convo_graph.add_state(
                create_convo_correct_answer_state(
                    statenum=statenum, worksheet_name=worksheet_name
                )
            )
    microlesson_name = data_from_df[0][0]
    convo_graph.add_state(create_convo_stop_state(microlesson_name))
    return convo_graph


def yml_parse_create_single_convograph(file_path: str) -> ConvoGraph:
    parser = ConvoDataParser()
    dfs, worksheet_names = parser.parse(file_path=file_path)

    for index, df in enumerate(dfs):
        convo_graph = ConvoGraph(worksheet_name_source_data=worksheet_names[index])
        convo_graph.populate_convo(df)

    return convo_graph
