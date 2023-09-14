import re
from abc import ABC, abstractmethod


class Sorter(ABC):
    @abstractmethod
    def sort(self, input_data: list[str]):
        pass


class WorkSheetsSorter(Sorter):
    def sort(self, worksheets) -> list:
        """Sorts worksheets in provided workbook with predefined lesson order logic

        Args:
            workbook (openpyxl.Workbook): Loaded .xlsx file

        Returns:
            None: Blank return
        """

        pattern = r"G(\d+)[._](\w+)[._](\d+)[._](\d+)[._](\d+)"

        grouped_lessons = {}

        for sheet_name in worksheets:
            match = re.search(pattern, sheet_name)
            if match:
                grade = int(match.group(1))
                domain = match.group(2)
                n1 = int(match.group(3))
                n2 = int(match.group(4))
                n3 = int(match.group(5))

                if domain not in grouped_lessons:
                    grouped_lessons[domain] = []

                grouped_lessons[domain].append((sheet_name, grade, n1, n2, n3))

        sorted_worksheets = []

        for _, lessons in sorted(grouped_lessons.items()):
            sorted_lessons = sorted(lessons, key=lambda x: (x[1], x[2], x[3], x[4]))
            sorted_worksheets.extend(
                [sheet_name for sheet_name, _, _, _, _ in sorted_lessons]
            )

        return sorted_worksheets


class YAMLFileNamesSorter(Sorter):
    def sort(self, file_names) -> list:
        """Sorts list of .yml file_names in predefined order logic

        Args:
            file_names (list): Unsorted list of file_names

        Returns:
            list: Sorted list of file_names
        """

        pattern = r"G(\d+)[._](\w+)[._](\d+)[._](\d+)[._](\d+)"

        grouped_file_names = {}

        other_file_names_different_format = []

        for file_name in file_names:
            match = re.search(pattern, file_name)
            if match:
                grade = int(match.group(1))
                domain = match.group(2)
                n1 = int(match.group(3))
                n2 = int(match.group(4))
                n3 = int(match.group(5))

                if domain not in grouped_file_names:
                    grouped_file_names[domain] = []

                grouped_file_names[domain].append((file_name, grade, n1, n2, n3))
            else:
                other_file_names_different_format.append(file_name)
        sorted_file_names = []

        for _, lessons in sorted(grouped_file_names.items()):
            sorted_lessons = sorted(lessons, key=lambda x: (x[1], x[2], x[3], x[4]))
            sorted_file_names.extend(
                [sheet_name for sheet_name, _, _, _, _ in sorted_lessons]
            )

        sorted_file_names.extend(other_file_names_different_format)

        return sorted_file_names
