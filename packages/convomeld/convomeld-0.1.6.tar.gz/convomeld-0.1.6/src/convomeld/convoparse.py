import argparse
import os

from convomeld.df_to_convograph import create_convograph
from convomeld.xlsx_csv_parsers import ConvoDataParser
from convomeld.utils import YAMLWriter


def main():
    parser = argparse.ArgumentParser(
        description="Parse XLSX and CSV files in a folder, create convo_graphs and convert them to YAML files."
    )
    parser.add_argument(
        "file_paths",
        nargs="+",
        help="Paths to the XLSX or CSV files containing convo_graph specific format data",
    )
    parser.add_argument(
        "--dest_folder",
        "-d",
        help="Path to the destination folder where YAML files will be created.",
    )

    args = parser.parse_args()

    parsed_dfs = []
    parsed_worksheet_names = []
    parser = ConvoDataParser()

    for file_path in args.file_paths:
        dfs, worksheet_names = parser.parse(file_path=file_path)
        parsed_dfs.extend(dfs)
        parsed_worksheet_names.extend(worksheet_names)

    worksheet_names_dfs = dict(zip(parsed_worksheet_names, parsed_dfs))

    for worksheet_name in worksheet_names_dfs.keys():
        convo_graph = create_convograph(
            worksheet_names_dfs[worksheet_name], worksheet_name
        )
        if args.dest_folder:
            YAMLWriter.write_convograph_to_yaml_file(
                convo_graph.to_list_of_dicts(), file_path=args.dest_folder
            )
        else:
            YAMLWriter.write_convograph_to_yaml_file(
                convo_graph.to_list_of_dicts(), file_path=os.getcwd()
            )


if __name__ == "__main__":
    main()
