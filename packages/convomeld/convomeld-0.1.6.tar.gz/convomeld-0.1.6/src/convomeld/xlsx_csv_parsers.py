import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple, Union
import os
import pandas as pd
import yaml


class Parser(ABC):
    @abstractmethod
    def parse(self, path: str):
        pass


class ConvoDataParser(Parser):
    """Class that provides methods to parse different file formats"""

    @staticmethod
    def __parse_csv(file_path: str) -> Tuple[List[pd.DataFrame], List[str]]:
        try:
            file_name = os.path.basename(file_path).split(".")[0]

            data = pd.read_csv(file_path, dtype="str")
            data = data.dropna(how="all")
            data = [data.columns.tolist()] + data.values.tolist()
            df = pd.DataFrame(data)

            return [df], [file_name]
        except Exception as e:
            print(f"Error parsing CSV: {e}")
            return []

    @staticmethod
    def __parse_xlsx(file_path: str) -> Tuple[List[pd.DataFrame], List[str]]:
        def convert_to_fraction(value):
            if isinstance(value, datetime.datetime):
                value = value.strftime("%-d/%-m")
                return value
            return value

        try:
            dfs_xlsx_file = []

            xlsx_file = pd.ExcelFile(file_path)
            worksheet_names = xlsx_file.sheet_names

            for sheet_name in worksheet_names:
                df = pd.read_excel(xlsx_file, sheet_name=sheet_name, header=None)
                df[4] = df[4].apply(convert_to_fraction)
                sheet_data = df.dropna(how="any")

                dfs_xlsx_file.append(sheet_data)
            return dfs_xlsx_file, worksheet_names
        except Exception as e:
            print(f"Error parsing Excel file: {e}")
            return []

    @staticmethod
    def __parse_yml(file_path: str) -> Tuple[List[List], List[str]]:
        file_name = os.path.basename(file_path).rstrip(".yml")

        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        return [yaml_data], [file_name]

    def parse(
        self, file_path: Union[str, Path]
    ) -> Union[Tuple[List[pd.DataFrame], List[str]], Tuple[List[List], List[str]]]:
        file_name = os.path.basename(file_path)
        if file_name.endswith(".csv"):
            return self.__parse_csv(file_path=file_path)
        elif file_name.endswith(".xlsx"):
            return self.__parse_xlsx(file_path=file_path)
        elif file_name.endswith(".yml"):
            return self.__parse_yml(file_path=file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_name}")


class YAMLFileNamesParser(Parser):
    def parse(self, args_path: list) -> dict:
        """Parse and return list of filenames which has .yml format"""
        file_name_file_path = {}
        for path in args_path:
            if os.path.isfile(path) and path.lower().endswith(".yml"):
                file_name_file_path[os.path.basename(path)] = path
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.lower().endswith(".yml"):
                            file_name_file_path[file] = os.path.join(root, file)
        return file_name_file_path


class XLSXFileNamesParser(Parser):
    def parse(self, folder_path: str) -> list[str]:
        """Parse folder and return list of filenames which has .xlsx format"""
        files_list = []
        for filename in os.listdir(folder_path):
            if os.path.isfile(
                os.path.join(folder_path, filename)
            ) and filename.endswith(".xlsx"):
                files_list.append(filename)
        return files_list


class CSVFileNamesParser(Parser):
    def parse(self, folder_path: str) -> list[str]:
        """Parse folder and return list of filenames which has .csv format"""
        files_list = []
        for filename in os.listdir(folder_path):
            if os.path.isfile(
                os.path.join(folder_path, filename)
            ) and filename.endswith(".csv"):
                files_list.append(filename)
        return files_list
