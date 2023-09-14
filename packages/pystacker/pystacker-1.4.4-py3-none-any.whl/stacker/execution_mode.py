from __future__ import annotations

import copy
import logging
import sys
import traceback

from pathlib import Path

from stacker.util import colored
from stacker.stacker import Stacker
from stacker.lib.config import history_file_path
from stacker.lib import (
    show_about,
    show_help,
    show_help_jp,
    show_top,
    delete_history
)
from stacker.util.string_parser import (
    is_brace_balanced,
    is_tuple_balanced,
    is_array_balanced,
    is_tuple,
    is_array
)

from pkg_resources import get_distribution
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit import prompt


class ExecutionMode:
    def __init__(self, rpn_calculator: Stacker):
        self.rpn_calculator = rpn_calculator
        self._operator_key = list(self.rpn_calculator.operator.keys())
        self._variable_key = list(self.rpn_calculator.variables.keys())
        self._reserved_word = copy.deepcopy(self.rpn_calculator.reserved_word)
        self._reserved_word = (self._reserved_word + self._operator_key + self._variable_key)
        self.completer = WordCompleter(self._reserved_word)
        self.color_print = True
        self.dmode = False

    def debug_mode(self):
        self.dmode = True

    def get_multiline_input(self, prompt="") -> str:
        lines = []
        while True:
            line = input(prompt)
            if line.endswith("\\"):
                line = line[:-1]  # バックスラッシュを取り除く
                lines.append(line)
                prompt = ""  # 2行目以降のプロンプトは空にする
            else:
                lines.append(line)
                break
        return "\n".join(lines)

    def run(self):
        raise NotImplementedError("Subclasses must implement the 'run' method")

    def print_colored_output(self, stack_list) -> None:
        stack_str = colored("[", 'yellow')
        for item in stack_list:
            item_str = str(item)
            # print(item_str)
            if item_str.startswith('[') or item_str.endswith(']'):
                stack_str += colored(item_str, 'red')
                stack_str += ", "
            elif item_str.startswith('(') or item_str.endswith(')'):
                stack_str += colored(item_str, 'green')
                stack_str += ", "
            elif item_str.replace('.', '', 1).isdigit() or (item_str.startswith('-') and item_str[1:].replace('.', '', 1).isdigit()):
                stack_str += colored(item_str, 'default')
                stack_str += ", "
            elif item_str in list(self.rpn_calculator.variables.keys()):
                stack_str += colored(item_str, 'lightblue')
                stack_str += ", "
            else:
                stack_str += colored(item_str, 'default')
                stack_str += ", "
        stack_str = stack_str[0:-2]
        stack_str += colored("]", 'yellow')
        print(stack_str)

    def show_stack(self) -> None:
        """ Print the current stack to the console.
        """
        tokens = self.rpn_calculator.get_stack()
        if len(tokens) == 0:
            return
        stack = []
        for token in tokens:
            if isinstance(token, Stacker):
                stack.append(token.sub_expression)
            else:
                stack.append(token)

        if self.color_print is True:
            self.print_colored_output(stack)
        else:
            print(stack)


class InteractiveMode(ExecutionMode):

    def get_input(self, prompt_text: str, multiline: bool):
        try:
            return prompt(
                prompt_text,
                history=FileHistory(history_file_path),
                completer=self.completer,
                multiline=multiline
            )
        except EOFError:
            print("\nSee you!")
            sys.exit()

    def run(self):
        show_top()
        stacker_version = get_distribution('pystacker').version
        print(f"Stacker {stacker_version} on {sys.platform}")
        print('Type "help" or "help-jp" to get more information.')

        line_count = 0
        while True:
            try:
                expression = self.get_input(f"stacker:{line_count}> ", multiline=False)
                if expression[-2:] in {";]", ";)"}:
                    closer = expression[-1]
                    expression = expression[:-2] + closer

                if is_array(expression) or is_tuple(expression):
                    # """
                    #     # List
                    #     stacker:0> [1 2 3
                    #                 3 4 5]
                    #     [1 2 3; 3 4 5]

                    #     # Tuple
                    #     stacker:0> (1 2 3
                    #                 3 4 5)
                    #     (1 2 3; 3 4 5)
                    # """
                    while not is_array_balanced(expression) or not is_tuple_balanced(expression):
                        prompt_text = " " * (len(f"stacker:{line_count}> ") - len("> ")) + "> "
                        next_line = self.get_input(prompt_text, multiline=False)
                        if next_line.lower() == ('end'):
                            break
                        if next_line in {"]", ")"}:
                            expression += next_line
                            if is_array_balanced(expression) or is_tuple_balanced(expression):
                                if expression[-2:] in {";]", ";)"}:
                                    closer = expression[-1]
                                    expression = expression[:-2] + closer
                                break
                        if next_line[-2:] in {";]", ";)"}:
                            closer = next_line[-1]
                            next_line = next_line[:-2] + closer
                        if not expression.endswith(";"):
                            expression += "; " + next_line
                        else:
                            expression += " " + next_line

                # # ダブルコーテーションまたはシングルコーテーションで始まる入力が閉じられるまで継続する処理
                # while (
                #     (expression.startswith('"""') and expression.count('"""') % 2 != 0) or
                #     (expression.startswith("'''") and expression.count("'''") % 2 != 0)
                # ):
                #     """
                #         stacker:0> '''
                #         stacker:0> This is a multi-line
                #         stacker:0> input example.
                #         stacker:0> '''
                #         ['\nThis is a multi-line\ninput example.\n']
                #     """
                #     prompt_text = " " * (len(f"stacker:{line_count}> ") - len("> ")) + "> "
                #     next_line = self.get_input(prompt_text, multiline=False)
                #     expression += "\n" + next_line

                logging.debug("input expression: %s", expression)

                if expression.lower() == "exit":
                    break
                if expression.lower() == "help":
                    show_help()
                    print("")
                    print("Plugin commands:")
                    for plugin_name, plugin_descriptions in self.rpn_calculator.plugin_descriptions.items():
                        en_description = plugin_descriptions.get("en", None)
                        if en_description:
                            print(f"  {plugin_name}: {en_description}")
                    continue
                if expression.lower() == "help-jp":
                    show_help_jp()
                    print("")
                    print("プラグインコマンド：")
                    for plugin_name, plugin_descriptions in self.rpn_calculator.plugin_descriptions.items():
                        jp_description = plugin_descriptions.get("jp", None)
                        if jp_description:
                            print(f"  {plugin_name}: {jp_description}")
                        else:
                            print(f"  {plugin_name}: {plugin_descriptions['en']} (日本語の説明はありません)")
                    continue
                if expression.lower() == "about":
                    show_about()
                    continue
                if expression.lower() == "delete_history":
                    delete_history()
                    continue

                self.rpn_calculator.process_expression(expression)
                self.show_stack()

            except EOFError:
                print("\nSee you!")
                break

            except Exception as e:
                print(colored(f"[ERROR]: {e}", "red"))
                if self.dmode:
                    traceback.print_exc()

            line_count += 1


class ScriptMode(ExecutionMode):

    def __init__(self, rpn_calculator: Stacker):
        super().__init__(rpn_calculator)

    def run(self, file_path: str):
        path = Path(file_path)
        if not path.is_file() or not path.suffix == '.sk':
            raise ValueError("Invalid file path or file type. Please provide a valid '.sk' file.")

        with path.open('r') as script_file:
            expression = ''
            for line in script_file:
                line = line.strip()
                if line.startswith('#') or not line:  # ignore comments and empty lines
                    continue
                expression += line + ' '
                if self._is_balanced(expression):
                    if expression[-2:] in {";]", ";)"}:
                        closer = expression[-1]
                        expression = expression[:-2] + closer
                    self.rpn_calculator.process_expression(expression)
                    expression = ''

    def _is_balanced(self, expression: str) -> bool:
        return (
            is_array_balanced(expression) and
            is_tuple_balanced(expression) and
            is_brace_balanced(expression) and
            (expression.count('"""') % 2 == 0) and
            (expression.count("'''") % 2 == 0)
        )
