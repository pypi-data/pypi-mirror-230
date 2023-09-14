import argparse
import os

from convomeld.df_to_convograph import (
    yml_parse_create_single_convograph,
)
from convomeld.xlsx_csv_parsers import YAMLFileNamesParser
from convomeld.utils import YAMLWriter
from convomeld.sorters import YAMLFileNamesSorter


def main():
    parser = argparse.ArgumentParser(description="Concatenate YAML files in a folder.")
    parser.add_argument(
        "file_paths",
        nargs="+",
        help="Paths to the YAML files or folders containing YAML files.",
    )
    parser.add_argument(
        "--dest_folder",
        "-d",
        help="Path to the destination folder where concatenated YAML file will be created.",
    )
    args = parser.parse_args()

    files_names_parser = YAMLFileNamesParser()
    file_names_file_paths = files_names_parser.parse(args.file_paths)

    if not file_names_file_paths:
        print("No valid YAML files found in the provided paths.")
        return

    files_names_sorter = YAMLFileNamesSorter()
    sorted_file_names = files_names_sorter.sort(file_names_file_paths.keys())

    start_convograph = yml_parse_create_single_convograph(
        file_path=file_names_file_paths[sorted_file_names[0]]
    )

    for file_name in sorted_file_names[1:]:
        next_convograph = yml_parse_create_single_convograph(
            file_path=file_names_file_paths[file_name]
        )
        start_convograph += next_convograph

    if args.dest_folder:
        YAMLWriter.write_convograph_to_yaml_file(
            start_convograph.to_list_of_dicts(), file_path=args.dest_folder
        )
    else:
        YAMLWriter.write_convograph_to_yaml_file(
            start_convograph.to_list_of_dicts(), file_path=os.getcwd()
        )


if __name__ == "__main__":
    main()
