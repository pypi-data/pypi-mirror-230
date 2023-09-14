import argparse
import convomeld.graph


def cli():
    parser = argparse.ArgumentParser(
        prog="ConvoMerge",
        description="Allows to merge multiptle linear conversation files into single conversation tree",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Path(s) to input .txt or .yml linear conversation files",
    )
    parser.add_argument(
        "-o", "--output", help="Path to output .yml to store the result", required=True
    )
    parser.add_argument("-n", "--convo-name")
    parser.add_argument("-d", "--convo-description")
    parser.add_argument("-a", "--base-author", default="teacher")
    args = parser.parse_args()

    script_files = args.inputs
    output_file = args.output
    convo_name = args.convo_name
    convo_description = args.convo_description
    base_author = args.base_author

    base_graph = None

    for script_file in script_files:
        graph = convomeld.graph.ConvoGraph.from_file(
            script_file,
            convo_name=convo_name,
            convo_description=convo_description,
            base_author=base_author,
            use_uuid=True,
        )

        if base_graph is None:
            base_graph = graph
        else:
            base_graph = base_graph.merge_graph(graph)

    base_graph.to_yaml(output_file)
