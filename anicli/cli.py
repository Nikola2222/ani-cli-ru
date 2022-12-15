"""Preconfigured Cli class with help and exit commands"""
from typing import Optional, Union, Callable, List

from prompt_toolkit.shortcuts import confirm

from prompt_toolkit.auto_suggest import AutoSuggest
from prompt_toolkit.clipboard import Clipboard
from prompt_toolkit.completion import WordCompleter, Completer
from prompt_toolkit.cursor_shapes import AnyCursorShapeConfig
from prompt_toolkit.filters import FilterOrBool
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.history import History
from prompt_toolkit.key_binding import KeyBindingsBase
from prompt_toolkit.layout.processors import Processor
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.output import ColorDepth
from prompt_toolkit.shortcuts import CompleteStyle
from prompt_toolkit.shortcuts.prompt import PromptContinuationText
from prompt_toolkit.styles import BaseStyle, StyleTransformation
from prompt_toolkit.validation import Validator

from anicli.base import BaseDispatcher

def _exit(_):  # ctx dispatcher
    if confirm():
        exit(1)


def _help(ctx: BaseDispatcher, command: Optional[str] = None):
    if command:
        for cls_command in ctx.list_commands:
            if command in cls_command:
                print(f"{cls_command.keywords} - {cls_command.help}")
                return
        print("command", command, "not found.\n\tusage `help` for get list available commands")
    else:
        for cls_command in ctx.list_commands:
            print(f"{cls_command.keywords} {cls_command.help}")


class CliApp(BaseDispatcher):
    def __init__(self,
                 message: AnyFormattedText = "> ",
                 *,
                 is_password: FilterOrBool = False,
                 complete_while_typing: FilterOrBool = True,
                 validate_while_typing: FilterOrBool = True,
                 enable_history_search: FilterOrBool = False,
                 search_ignore_case: FilterOrBool = False,
                 lexer: Optional[Lexer] = None,
                 enable_system_prompt: FilterOrBool = False,
                 enable_suspend: FilterOrBool = False,
                 enable_open_in_editor: FilterOrBool = False,
                 validator: Optional[Validator] = None,
                 completer: Optional[Completer] = None,
                 complete_in_thread: bool = False,
                 reserve_space_for_menu: int = 8,
                 complete_style: CompleteStyle = CompleteStyle.COLUMN,
                 auto_suggest: Optional[AutoSuggest] = None,
                 style: Optional[BaseStyle] = None,
                 style_transformation: Optional[StyleTransformation] = None,
                 swap_light_and_dark_colors: FilterOrBool = False,
                 color_depth: Optional[ColorDepth] = None,
                 cursor: AnyCursorShapeConfig = None,
                 include_default_pygments_style: FilterOrBool = True,
                 history: Optional[History] = None,
                 clipboard: Optional[Clipboard] = None,
                 prompt_continuation: Optional[PromptContinuationText] = None,
                 rprompt: AnyFormattedText = None,
                 bottom_toolbar: AnyFormattedText = None,
                 mouse_support: FilterOrBool = False,
                 input_processors: Optional[List[Processor]] = None,
                 placeholder: Optional[AnyFormattedText] = None,
                 key_bindings: Optional[KeyBindingsBase] = None,
                 erase_when_done: bool = False,
                 tempfile_suffix: Optional[Union[str, Callable[[], str]]] = ".txt",
                 tempfile: Optional[Union[str, Callable[[], str]]] = None,
                 refresh_interval: float = 0,
                 ):
        super().__init__(
            message=message,
            is_password=is_password,
            complete_while_typing=complete_while_typing,
            validate_while_typing=validate_while_typing,
            enable_history_search=enable_history_search,
            search_ignore_case=search_ignore_case,
            lexer=lexer,
            enable_system_prompt=enable_system_prompt,
            enable_suspend=enable_suspend,
            enable_open_in_editor=enable_open_in_editor,
            validator=validator,
            completer=completer,
            complete_in_thread=complete_in_thread,
            reserve_space_for_menu=reserve_space_for_menu,
            complete_style=complete_style,
            auto_suggest=auto_suggest,
            style=style,
            style_transformation=style_transformation,
            swap_light_and_dark_colors=swap_light_and_dark_colors,
            color_depth=color_depth,
            cursor=cursor,
            include_default_pygments_style=include_default_pygments_style,
            history=history,
            clipboard=clipboard,
            prompt_continuation=prompt_continuation,
            rprompt=rprompt,
            bottom_toolbar=bottom_toolbar,
            mouse_support=mouse_support,
            input_processors=input_processors,
            placeholder=placeholder,
            key_bindings=key_bindings,
            erase_when_done=erase_when_done,
            tempfile_suffix=tempfile_suffix,
            tempfile=tempfile,
            refresh_interval=refresh_interval
        )

        self.add_command(_exit, keywords=["exit", "quit"], help_meta="exit this app")
        self.add_command(_help, keywords=["help"], help_meta="show help message")
