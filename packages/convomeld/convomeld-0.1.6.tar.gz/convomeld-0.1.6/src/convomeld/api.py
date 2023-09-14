from convomeld.graph import ConvoGraph


def script_to_graph(
    script: list[str],
    bot_name="bot",
    convo_name="convo_name",
    convo_description="empty",
    nlp="exact",
    normalized=True,
    version="v2",
) -> list[dict]:
    """Converts a human readable 'theater' script or conversation log to convoscript graph in v2 format
    >>> # Normal script
    >>> script_to_graph([
    ...     'bot: Hi!', 'bot: Is there anything I can help?', 'human: What time is it now?', 'bot: It is 12PM now', 'bot: Is there anything I can help?', 'human: No', 'bot: Fine, have a good day!'
    ... ])
    [{'name': 'start', 'convo_name': 'convo_name', 'convo_description': 'empty', 'nlp': 'exact', 'triggers': {'en': {'__next__': 'convo_name/respond_1'}}}, {'name': 'convo_name/respond_1', 'actions': {'en': ['Hi!']}, 'triggers': {'en': {'__next__': 'convo_name/question_1_1'}}}, {'name': 'convo_name/question_1_1', 'actions': {'en': ['Is there anything I can help?']}, 'triggers': {'en': {'__default__': 'convo_name/question_1_1', 'What time is it now?': 'convo_name/respond_2'}}}, {'name': 'convo_name/respond_2', 'actions': {'en': ['It is 12PM now']}, 'triggers': {'en': {'__next__': 'convo_name/question_1_2'}}}, {'name': 'convo_name/question_1_2', 'actions': {'en': ['Is there anything I can help?']}, 'triggers': {'en': {'__default__': 'convo_name/question_1_2', 'No': 'convo_name/respond_3'}}}, {'name': 'convo_name/respond_3', 'actions': {'en': ['Fine, have a good day!']}, 'triggers': {'en': {'__next__': 'stop'}}}, {'name': 'stop', 'triggers': {'en': {'__default__': 'start'}}}]
    >>> # Human stop early script
    >>> script_to_graph([
    ...     'bot: Hi!', 'bot: Is there anything I can help?', 'human: What time is it now?', 'bot: It is 12PM now', 'bot: Is there anything I can help?'
    ... ])
    [{'name': 'start', 'convo_name': 'convo_name', 'convo_description': 'empty', 'nlp': 'exact', 'triggers': {'en': {'__next__': 'convo_name/respond_1'}}}, {'name': 'convo_name/respond_1', 'actions': {'en': ['Hi!']}, 'triggers': {'en': {'__next__': 'convo_name/question_1_1'}}}, {'name': 'convo_name/question_1_1', 'actions': {'en': ['Is there anything I can help?']}, 'triggers': {'en': {'__default__': 'convo_name/question_1_1', 'What time is it now?': 'convo_name/respond_2'}}}, {'name': 'convo_name/respond_2', 'actions': {'en': ['It is 12PM now']}, 'triggers': {'en': {'__next__': 'convo_name/question_1_2'}}}, {'name': 'convo_name/question_1_2', 'actions': {'en': ['Is there anything I can help?']}, 'triggers': {'en': {'__timeout__': 'stop', '__default__': 'convo_name/question_1_2'}}}, {'name': 'stop', 'triggers': {'en': {'__default__': 'start'}}}]
    >>> # Bot stop early script
    >>> script_to_graph([
    ...     'bot: Hi!', 'bot: Is there anything I can help?', 'human: No'
    ... ])
    [{'name': 'start', 'convo_name': 'convo_name', 'convo_description': 'empty', 'nlp': 'exact', 'triggers': {'en': {'__next__': 'convo_name/respond_1'}}}, {'name': 'convo_name/respond_1', 'actions': {'en': ['Hi!']}, 'triggers': {'en': {'__next__': 'convo_name/question_1_1'}}}, {'name': 'convo_name/question_1_1', 'actions': {'en': ['Is there anything I can help?']}, 'triggers': {'en': {'__default__': 'convo_name/question_1_1', 'No': 'stop'}}}, {'name': 'stop', 'triggers': {'en': {'__default__': 'start'}}}]
    """

    graph = ConvoGraph.from_script_lines(
        script,
        convo_name=convo_name,
        convo_description=convo_description,
        nlp=nlp,
        base_author=bot_name,
        use_uuid=False,
        normalized=normalized
    )
    return graph.to_states_list(version)


def compare_graphs(graph1: list[dict], graph2: list[dict]) -> bool:
    """Compares a couple of convoscript graphs
    >>> # Normal script
    >>> graph1 = script_to_graph([
    ...     'bot: Hi!', 'bot: Is there anything I can help?', 'human: What time is it now?', 'bot: It is 12PM now', 'bot: Is there anything I can help?', 'human: No', 'bot: Fine, have a good day!'
    ... ])
    >>> compare_graphs(graph1, graph1)
    True
    >>> graph2 = script_to_graph([
    ...     'bot: Hi!', 'bot: Is there anything I can help?', 'human: No', 'bot: Fine, have a good day!'
    ... ])
    >>> compare_graphs(graph1, graph2)
    False
    """

    return ConvoGraph.from_states_list(graph1).compare(
        ConvoGraph.from_states_list(graph2)
    )


def normalize_graph(graph, input_version=None, output_version='v2'):
    graph = ConvoGraph.from_states_list(graph, version=input_version)
    norm_graph = graph.normalized()
    return norm_graph.to_states_list(version=output_version)


def file_to_graph(
    fp,
    convo_name=None,
    convo_description=None,
    nlp=None,
    text_script_parser=None,
    base_author=None,
    action_matcher=None,
    trigger_matcher=None,
    use_uuid=None,
    input_version=None,
    output_version="v2",
) -> list[dict]:
    graph = ConvoGraph.from_file(
        fp,
        convo_name,
        convo_description,
        nlp,
        text_script_parser,
        base_author,
        action_matcher,
        trigger_matcher,
        use_uuid,
        input_version,
    )
    return graph.to_states_list(output_version)


def merge_graphs(
    *graphs: list[dict],
    convo_name=None,
    convo_description=None,
    nlp=None,
    input_version=None,
    output_version="v2"
) -> list[dict]:
    base_graph = None

    if len(graphs) == 0:
        return []

    for graph in graphs:
        if base_graph is None:
            base_graph = ConvoGraph.from_states_list(
                graph,
                convo_name=convo_name,
                convo_description=convo_description,
                nlp=nlp,
                use_uuid=False,
                version=input_version,
            )
        else:
            base_graph = base_graph.merge_graph(
                ConvoGraph.from_states_list(
                    graph, use_uuid=False, version=input_version
                )
            )

    return base_graph.to_states_list(output_version)
