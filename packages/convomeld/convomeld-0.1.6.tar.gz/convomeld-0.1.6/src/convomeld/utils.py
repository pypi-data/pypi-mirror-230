import yaml


class YAMLWriter:
    @staticmethod
    def write_convograph_to_yaml_file(convograph_data: list, file_path: str) -> None:
        """Write down prepared sequence of microlessons structures to YAML file

        Args:
            convograph_data (list): Contains sequence of proccessed complete microlessons structures
            file_path (str): filepath of destination YAML file

        Returns:
            None: Blank return
        """
        file_name = (
            convograph_data[0]["convo_name"]
            if len(convograph_data[0]["convo_name"]) < 110
            else "merged_convographs"
        )
        yaml_file_path = f"{file_path}/{file_name}.yml"

        with open(yaml_file_path, "w") as file:

            class MyDumper(yaml.SafeDumper):
                """Class that helps put space between blocks in YML file"""

                def write_line_break(self, data=None):
                    super().write_line_break(data)

                    if len(self.indents) == 1:
                        super().write_line_break()

            yaml.dump(
                convograph_data,
                file,
                default_flow_style=False,
                sort_keys=False,
                Dumper=MyDumper,
            )
