import numpy as np
import pandas as pd
import sys

from constants import DATA_DIR
from pathlib import Path

DEFAULT_CSV_PATH = DATA_DIR / "example_conversation.csv"


class BaseCard:
    def __init__(self, index, row, df):
        self.df = df
        self.row = row
        self.row_num = index + 1  # Index
        self.row_type = row["Type"]  # Column A
        self.bot_content = row["Bot says"]  # Column B
        self.user_content = row["User says"]  # Column C
        self.go_to = row["Go to"]  # Column D
        self.go_to_row_num = row["Go to Row Number"]  # Column E
        self.variable_name = row["Save to Variable"]  # Column F
        self.variable_action = row["Variable Action"]  # Column G
        self.fallback = row["Fallback Strategy"]  # Column H
        self.link = row["Links"]  # Column I
        self.card_title = f"Row{index+2}"
        (
            self.variable_update,
            self.variable_statement,
        ) = self.parse_variable_actions_to_template()
        self.fallback_message = self.df.iloc[0]["Reprompt Fallback Message"]

    def parse_variable_actions_to_template(self):
        variable_update = ""
        variable_statement = ""
        if self.variable_name:
            if self.variable_action == 0 or self.variable_action is None:
                variable_update = f'update_contact({self.variable_name}: "@response")'
            if (
                self.variable_name != None
                and self.variable_action != None
                and self.variable_name != 0
                and self.variable_action != 0
            ):
                var_name_arr = self.variable_name.split(", ")
                var_action_arr = self.variable_action.split(", ")

                if len(var_name_arr) == len(var_action_arr):
                    for i in range(len(var_name_arr)):
                        action = "= 0"
                        if var_action_arr[i] == "Set 0":
                            action = f"{var_name_arr[i]} = 0"
                        if var_action_arr[i] == "Set True":
                            action = f"{var_name_arr[i]} = True"
                        if var_action_arr[i] == "Add 1":
                            action = f"{var_name_arr[i]} = {var_name_arr[i]} + 1"
                        if var_action_arr[i] == "Save":
                            action = f'update_contact({var_name_arr[i]}: "@{var_name_arr[i]}")'
                        variable_statement += f"""
        {action}
        """
        return variable_update, variable_statement

    def create_fallback_card(self):
        fallback_card_name = f"Row{self.row_num}Fallback"

        card = f'''
    card {fallback_card_name} when fallback == True, then: Row{self.row_num} do
    fallback = False

    text("""
    {self.fallback_message}
    """)
    end
        '''
        return card

    def set_run_stack_value(self, stack_uuid, value=""):
        """Sets a stack UUID or returns the default value

        >>> set_run_stack_value(None, '')
        ''
        >>> set_run_stack_value("da78ad789adg789ag", '')
        "da78ad789adg789ag"
        """
        if stack_uuid:
            value = f'run_stack("{stack_uuid}")'
        return value

    def set_skip_card_name(self, fallback_method, fallback_row_num):
        card_name = ""
        if fallback_method == "Reprompt":
            card_name = f"Row{fallback_row_num}Fallback"
        return card_name

    def create_skip_card(
        self,
        row_num,
        go_to_row_num,
        skip_trigger,
        variable_name=None,
        skip_link=None,
        fallback_method=None,
        fallback_row_num=None,
        regular_go_to=None,
        card_type="Skip",
    ):
        """Note: The variables in the skip card vary significantly
        ...depending on what type of card they come from,
        ...so they do not use the BaseCard self variables"""
        trigger_arr = []

        card_name = self.set_skip_card_name(fallback_method, fallback_row_num)

        # If there is a skip, build the variations of skip key word
        if isinstance(skip_trigger, str):
            trigger_arr.append(f'response == "{skip_trigger.lower()}"')
            trigger_arr.append(f'response == "{skip_trigger.capitalize()}"')
            trigger_arr.append(f'response == "{skip_trigger.upper()}"')

            skip_triggers_positive = " or ".join(trigger_arr)

            negative_arr = [x.replace("==", "!=") for x in trigger_arr]

            skip_triggers_negative = " and ".join(negative_arr)

        # If the skip triggers a link and the fallback is a reprompt
        if skip_link and fallback_method == "Reprompt":
            SkipTemplate = f"""   
    card {card_name} when {skip_triggers_positive} do
    run_stack("{skip_link}")
    end
    """
            return SkipTemplate

        # If the skip goes to another row and the fallback is a reprompt
        if fallback_method == "Reprompt":
            SkipTemplate = f"""   
    card {card_name} when {skip_triggers_positive}, then: Row{go_to_row_num} do
    log("Placeholder")
    end
    """
            return SkipTemplate
        if card_type == "ImageSkip":
            card_name = f"Row{row_num}Skip"
            next_card_name = f"Row{regular_go_to + 1}"
        else:
            card_name = f"Row{row_num}"
            next_card_name = f"Row{regular_go_to}"
            # Anything under here will get triggered for 'pass' fallback or no fallback (but skip present)
        if skip_link:
            skip_positive_conditions_card = f"""   
    card {card_name} when {skip_triggers_positive} do
    run_stack("{skip_link}")
    end
    """
        else:
            skip_positive_conditions_card = f"""   
    card {card_name} when {skip_triggers_positive}, then: Row{go_to_row_num} do
    log("Placeholder")
    end
    """
        update_contact = ""
        if variable_name:
            update_contact = f'update_contact({variable_name}: "@response")'

        SkipTemplate = f"""   
    {skip_positive_conditions_card}

    card {card_name} when {skip_triggers_negative}, then: {next_card_name} do
    log("Placeholder")

    {update_contact}
    end
        """
        return SkipTemplate

    def set_fallback_row_reference(
        self, row_fallback_info, row_num, go_to_row_nums, card_type
    ):
        skip_go_to_row_num = row_fallback_info.get("skip_go_to_row_num", None)
        fallback_method = row_fallback_info.get("fallback_method", None)
        skip_trigger_exists = row_fallback_info.get("skip_trigger_exists", False)
        go_to_row_numbers = row_fallback_info.get("row_fallback_info", None)

        fallback_go_to = ""
        fallback_boolean = ""
        if skip_trigger_exists and fallback_method != "Reprompt":
            fallback_go_to = f", then: Row{row_num}Skip"
        elif skip_go_to_row_num and fallback_method != "Reprompt":
            fallback_go_to = f", then: Row{skip_go_to_row_num}"
        elif fallback_method == "Pass" and card_type == "List":
            if skip_go_to_row_num:
                fallback_go_to = f", then: {skip_go_to_row_num}"
            else:
                fallback_go_to = f", then: {go_to_row_nums[0]}"
        elif fallback_method == "Pass":
            fallback_go_to = f", then: {go_to_row_nums[0]}"
        elif fallback_method == "Reprompt":
            fallback_go_to = f", then: Row{row_num}Fallback"
            fallback_boolean = "fallback = True"
        return fallback_go_to, fallback_boolean


class TextCard(BaseCard):
    def __init__(self, base_card):
        self.base = base_card

    def process_row(self):
        card = ""
        if self.base.go_to_row_num:
            card = self.build_continuing_card()
        elif self.base.go_to == 0 or self.base.go_to is False:
            card = self.build_terminal_card()
        return card

    def build_continuing_card(self):
        message = ""
        if self.base.bot_content and self.base.bot_content != "":
            message = f'''text("""
    {self.base.bot_content}
    """)'''
        link = self.base.set_run_stack_value(self.base.link)  # Stack UUID
        go_to_row_num_condition = f", then: Row{self.base.go_to_row_num}"

        return self.build_card_from_template(message, link, go_to_row_num_condition)

    def build_terminal_card(self):
        message = ""
        if self.base.bot_content:
            message = f'''text("""
    {self.base.bot_content}
    """)'''
        link = self.base.set_run_stack_value(self.base.link)

        return self.build_card_from_template(message, link)

    def build_card_from_template(self, message, link, go_to_row_num_condition=""):
        card = f"""
    card Row{self.base.row_num}{go_to_row_num_condition} do
    {message}
    {link}
    end
        """
        return card


class ImageCard(BaseCard):
    def __init__(self, base_card, index):
        self.base = base_card
        self.index = index

    def process_row(self):
        i = self.base.row_num
        image_row_num = self.base.row_num

        row_check = True
        while row_check:
            i += 1
            prev_row = i - 1
            if self.base.df.loc[prev_row, "Type"] == "Text":
                text = self.base.df.loc[prev_row]["Bot says"]
                go_to = self.base.df.loc[prev_row]["Go to Row Number"]

                card = self.build_image_text_card(go_to, text)

                row_check = False
                skip_row = self.base.row_num
            elif self.base.df.loc[prev_row, "Type"] == "Button Prompt":
                buttons_arr = []
                j = i
                button_check = True
                text = self.base.df.loc[prev_row]["Bot says"]
                fallback = self.base.df.loc[prev_row]["Fallback Strategy"]
                skip_row = self.base.row_num

                while button_check:
                    j += 1
                    prev_button_check_row = j - 1

                    skip_row_num = None
                    skip_trigger_bool = False
                    if self.base.df.loc[prev_button_check_row, "Type"] == "Skip":
                        skip_trigger_bool = True
                        skip_trigger = self.base.df.loc[prev_button_check_row][
                            "User says"
                        ]
                        skip_variable = self.base.df.loc[prev_button_check_row][
                            "Save to Variable"
                        ]
                        skip_link = self.base.df.loc[prev_button_check_row]["Links"]

                        skip_row_num = j
                        skip_go_to_row = self.base.df.loc[prev_button_check_row][
                            "Go to Row Number"
                        ]
                        go_to = skip_go_to_row
                        regular_go_to = self.base.row_num + 1

                    if self.base.df.loc[prev_button_check_row, "Type"] == "Button":
                        buttons_arr.append(f"Row{j}")
                    else:
                        button_check = False
                        row_check = False

                if fallback == 0:
                    fallback = None

                variable_action = None
                if self.base.variable_action == 0:
                    self.base.variable_action = None

                row_fallback_info = {
                    "skip_go_to_row_num": skip_row_num + 1,
                    "fallback_method": self.base.fallback,
                    "skip_trigger_exists": False,
                    "go_to_row_nums": buttons_arr,
                }

                card = self.build_image_button_card(
                    buttons_arr, text, row_fallback_info
                )

                if skip_trigger_bool:
                    card += self.base.create_skip_card(
                        image_row_num,
                        skip_go_to_row,
                        skip_trigger,
                        skip_variable,
                        skip_link,
                        fallback,
                        self.base.row_num,
                        regular_go_to,
                        "ImageSkip",
                    )

                if fallback == "Reprompt":
                    card += self.base.create_fallback_card()

        return card

    def build_image_text_card(self, go_to_row_num, text):
        card = f'''
    card Row{self.base.row_num}, then: Row{go_to_row_num} do
    image("{self.base.link}")

    text("""
    {text}
    """)
    end
        '''
        return card

    def build_image_button_card(self, go_to_row_nums, text, row_fallback_info=None):
        fallback_go_to, fallback_boolean = self.base.set_fallback_row_reference(
            row_fallback_info, self.base.row_num, go_to_row_nums, card_type="Button"
        )

        str = ", ".join(go_to_row_nums)

        ImageTemplate = f'''   
    card Row{self.base.row_num} {fallback_go_to} do
    {self.base.variable_update}
    response = buttons([{str}]) do
        image("{self.base.link}")
        text("""
        {text}
        """)
    end
    {fallback_boolean}
    end
        '''
        return ImageTemplate


class UserInputCard(BaseCard):
    def __init__(self, base_card):
        self.base = base_card

    def process_row(self):
        go_to = self.base.df.loc[self.base.row_num + 2 - 2, "Go to Row Number"]

        next_row_type = self.base.df.loc[self.base.row_num + 1, "Type"]

        skip_trigger_bool = False
        if next_row_type == "Skip":
            skip_trigger_bool = True
            skip_trigger = self.base.df.loc[self.base.row_num + 1, "User says"]

            skip_row_num = self.base.row_num + 2
            skip_go_to_row = self.base.df.loc[self.base.row_num + 1, "Go to Row Number"]
            go_to = skip_row_num
            regular_go_to = self.base.df.loc[
                self.base.row_num + 2 - 2, "Go to Row Number"
            ]

        card = self.build_card_from_template(go_to, skip_trigger_bool)

        if skip_trigger_bool:
            card += self.base.create_skip_card(
                skip_row_num,
                skip_go_to_row,
                skip_trigger,
                self.base.variable_name,
                None,
                None,
                None,
                regular_go_to,
            )
        return card

    def build_card_from_template(self, go_to, skip_present=False):
        variable_text = ""
        if self.base.variable_name:
            if skip_present == False:
                variable_text = (
                    f'update_contact({self.base.variable_name}: "@response")'
                )

        next_card = f", then: Row{go_to}"

        card = f'''
    card Row{self.base.row_num}{next_card} do
    response =
        ask("""
        {self.base.bot_content}
        """)
    {variable_text}
    end
    '''
        return card


class ListMenuCard(BaseCard):
    def __init__(self, base_card):
        self.base = base_card

    def process_row(self):
        menu_header = ""
        menu_footer = ""
        menu_title = ""

        menu_option_row_nums = []
        menu_options = []

        menu_option_cards = []

        i = self.base.row_num
        row_check = True
        skip_trigger_bool = False
        skip_row_label = None

        while row_check:
            i += 1
            prev_row = i - 1
            try:
                row_type = self.base.df.loc[prev_row, "Type"]
            except:
                break
            if row_type == "List Menu Title":
                menu_title = self.base.df.loc[prev_row]["Bot says"]
            elif row_type == "List Menu Header":
                menu_header = self.base.df.loc[prev_row]["Bot says"]
            elif row_type == "List Menu Footer":
                menu_footer = self.base.df.loc[prev_row]["Bot says"]
            elif row_type == "List Menu Option":
                menu_option_row_nums.append(
                    self.base.df.loc[prev_row]["Go to Row Number"]
                )
                menu_options.append(f"Row{i}")
                menu_option_card = self.MenuOptionCard(
                    i,
                    self.base.df.loc[prev_row, "User says"],
                    self.base.df.loc[prev_row, "Go to Row Number"],
                    self.base.df.loc[prev_row, "Links"],
                )
                menu_option_cards.append(menu_option_card)
            elif row_type == "Skip":
                skip_trigger_bool = True
                skip_trigger = self.base.df.loc[prev_row]["User says"]
                skip_row_num = i
                skip_row_label = f"Row{i}"
                skip_go_to_row = self.base.df.loc[prev_row]["Go to Row Number"]
                skip_variable = self.base.df.loc[prev_row]["Save to Variable"]
                skip_link = self.base.df.loc[prev_row]["Links"]
            else:
                row_check = False

        fallback = self.base.fallback

        if fallback == 0:
            fallback = None

        card = self.build_card_from_template(
            menu_options, menu_title, menu_header, menu_footer, fallback, skip_row_label
        )

        for menu_card in menu_option_cards:
            card += menu_card

        if skip_trigger_bool:
            card += self.base.create_skip_card(
                skip_row_num,
                skip_go_to_row,
                skip_trigger,
                skip_variable,
                skip_link,
                fallback,
                self.base.row_num,
                menu_option_row_nums[0],
            )

        if self.base.fallback == "Reprompt":
            card += self.base.create_fallback_card()

        return card

    def MenuOptionCard(self, row_num, button_text, go_to_row_num, stack_uuid=None):
        content = self.base.set_run_stack_value(stack_uuid, value='log("Placeholder")')

        go_to = f", then: Row{go_to_row_num}"
        if go_to_row_num == 0:
            go_to = ""

        buttonOptionTemplate = f"""
    card Row{row_num}, "{button_text}" {go_to} do
    {content}

    end
        """
        return buttonOptionTemplate

    def build_card_from_template(
        self, options, title, header, footer, fallback=None, skip_row_num=None
    ):
        menu_text = f'text("{self.base.bot_content}")'
        menu_header = f'header("{header}")'
        menu_footer = f'footer("{footer}")'
        menu_options = str = ", ".join(options)

        fallback_go_to = ""
        fallback_boolean = ""
        if fallback == "Pass":
            if skip_row_num:
                fallback_go_to = f", then: {skip_row_num}"
            else:
                fallback_go_to = f", then: {options[0]}"
        elif fallback == "Reprompt":
            fallback_go_to = f", then: Row{self.base.row_num}Fallback"
            fallback_boolean = "fallback = True"

        menuCardTemplate = f"""
    card Row{self.base.row_num} {fallback_go_to} do
    response = list("{title}", [{menu_options}]) do
        {menu_text}
        {menu_header}
        {menu_footer}
    end
    {fallback_boolean}
    end
    """
        return menuCardTemplate


class ButtonCard(BaseCard):
    def __init__(self, base_card):
        self.base = base_card

    def process_row(self):
        buttons_arr = []
        i = self.base.row_num
        row_check = True

        # Prevents an error if a button is the last item in the script
        try:
            next_row_type = self.base.df.loc[self.base.row_num + 1, "Type"]
        except KeyError:
            next_row_type = ""

        while row_check:
            i += 1
            prev_row = i - 1

            try:
                button_check = (self.base.df.iloc[[i - 2]]["Type"] == "Button").bool()
            except IndexError:
                button_check = False

            try:
                row_type = self.base.df.loc[prev_row, "Type"]
            except KeyError:
                row_type = ""

            skip_row_num = None
            skip_trigger_bool = False

            if row_type == "Skip":
                skip_trigger_bool = True
                skip_trigger = self.base.df.loc[prev_row, "User says"]
                skip_variable = self.base.df.loc[prev_row, "Save to Variable"]
                skip_link = self.base.df.loc[prev_row, "Links"]

                skip_row_num = i
                skip_go_to_row = self.base.df.loc[prev_row, "Go to Row Number"]
                go_to = skip_go_to_row
                regular_go_to = self.base.row_num + 1

            if button_check:
                buttons_arr.append(f"Row{i}")
            else:
                row_check = False

        if self.base.fallback == 0:
            self.base.fallback = None

        if self.base.variable_action == 0:
            self.base.variable_action = None

        row_fallback_info = {
            "skip_go_to_row_num": skip_row_num,
            "fallback_method": self.base.fallback,
            "skip_trigger_exists": False,
            "go_to_row_nums": buttons_arr,
        }

        fallback_go_to, fallback_boolean = self.base.set_fallback_row_reference(
            row_fallback_info, self.base.row_num, buttons_arr, card_type="Button"
        )

        card = self.build_card_from_template(
            buttons_arr, fallback_boolean, fallback_go_to
        )

        if skip_trigger_bool:
            card += self.base.create_skip_card(
                skip_row_num,
                skip_go_to_row,
                skip_trigger,
                skip_variable,
                skip_link,
                self.base.fallback,
                self.base.row_num,
                regular_go_to,
            )

        if self.base.fallback == "Reprompt":
            card += self.base.create_fallback_card()

        return card

    def build_card_from_template(self, buttons_arr, fallback_boolean, fallback_go_to):
        card = f'''
            card Row{self.base.row_num} {fallback_go_to} do
            {self.base.variable_statement}
            response = buttons([{", ".join(buttons_arr)}]) do
                text("""
                {self.base.bot_content}
                """)
            end
            {fallback_boolean}
            end    
            '''
        return card


class ButtonOptionCard(BaseCard):
    def __init__(self, base_card):
        self.base = base_card

    def process_row(self):
        if self.base.variable_name == 0:
            self.base.variable_name = None

        if self.base.variable_action == 0:
            self.base.variable_action = None

        card = self.build_card_from_template()

        return card

    def build_card_from_template(self):
        content = self.base.set_run_stack_value(
            self.base.link, value='log("Placeholder")'
        )

        go_to = f", then: Row{self.base.go_to_row_num}"
        if self.base.go_to_row_num == 0:
            go_to = ""

        card = f"""
    card Row{self.base.row_num}, "{self.base.user_content}" {go_to} do
    {self.base.variable_statement}
    {content}
    {self.base.variable_update}
    end
        """
        return card


def evaluate_card_type_of_row(index, row_data, base_card):
    if row_data["user_content"] == "<user input>":
        card = ""
    elif row_data["row_type"] == "Text":
        card_info = TextCard(base_card)
        card = card_info.process_row()
    elif row_data["row_type"] == "Image":
        card_info = ImageCard(base_card, index)
        card = card_info.process_row()
    elif row_data["row_type"] == "Button Prompt":
        card_info = ButtonCard(base_card)
        card = card_info.process_row()
    elif row_data["row_type"] == "Button":
        card_info = ButtonOptionCard(base_card)
        card = card_info.process_row()
    elif row_data["row_type"] == "User Input Prompt":
        card_info = UserInputCard(base_card)
        card = card_info.process_row()
    elif row_data["row_type"] == "List Menu":
        card_info = ListMenuCard(base_card)
        card = card_info.process_row()
    else:
        card = ""

    return card


def get_values_for_a_row(index, row):
    row_data = {
        "row_num": index + 1,  # Index
        "row_type": row["Type"],  # Column A
        "bot_content": row["Bot says"],  # Column B
        "user_content": row["User says"],  # Column C
        "go_to": row["Go to"],  # Column D
        "go_to_row_num": row["Go to Row Number"],  # Column E
        "variable_name": row["Save to Variable"],  # Column F
        "variable_action": row["Variable Action"],  # Column G
        "fallback": row["Fallback Strategy"],  # Column H
        "link": row["Links"],  # Column I
        "notes": row["Notes/comments"],  # Column J
        "card_title": f"Row{index+2}",
    }
    return row_data


def loop_through_df_rows(script_df):
    card_arr = []
    for index, row in script_df.iterrows():
        if index == 0:
            continue

        card_info = BaseCard(index, row, script_df)
        row_data = get_values_for_a_row(index, row)

        card = evaluate_card_type_of_row(index, row_data, card_info)

        card_arr.append(card)
    return card_arr


def read_and_preprocess_spreadsheet(uploaded_file):
    df = pd.read_csv(uploaded_file, header=None)

    df.columns = df.loc[0]
    df = df.loc[1:]

    script_df = df.fillna(0)
    script_df = script_df.replace("", 0)
    script_df["Go to Row Number"] = script_df["Go to Row Number"].apply(np.int64)
    return script_df


def write_file(card_arr):
    with open("refactoring_test.txt", "w", encoding="utf-8") as f:
        for card in card_arr:
            if not card.strip():
                continue
            f.write(card.strip() + "\n")
    return "\n".join(card_arr)


def convert(path=DEFAULT_CSV_PATH):
    """Convert csv file to Turn.IO Stacks text file"""
    script_df = read_and_preprocess_spreadsheet(DEFAULT_CSV_PATH)
    card_arr = loop_through_df_rows(script_df)
    return write_file(card_arr)


if __name__ == "__main__":
    path = DEFAULT_CSV_PATH
    if len(sys.argv) > 1:
        path = Path(sys.arg[1])
    print(convert(path=path))
