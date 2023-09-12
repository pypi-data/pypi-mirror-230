"""
Copyright 2023, Thomas Mahé <contact@tmahe.dev>
SPDX-License-Identifier: MIT
"""

import argparse
import inspect
import typing

from termkit.arguments import _TermkitArgument

__BUILTIN_TYPES__ = [str, int, float, complex, bool]


class TermkitParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._optionals.title = "Options"
        self._positionals.title = "Positionals"

        if kwargs.get("formatter_class", None) is None:
            self.formatter_class = argparse.RawTextHelpFormatter


class ArgumentHandler:
    def __init__(self, parser: argparse.ArgumentParser, func: typing.Callable):
        self.parser = parser
        self._func = func
        self.parameters = inspect.signature(func).parameters

    def parse(self, param_name: str):
        param = self.parameters.get(param_name)
        param_type = self._get_parameter_type(param_name)

        # f(param (= ...))
        if param.annotation is inspect.Parameter.empty:
            # f(param)
            if param.default is inspect.Parameter.empty:
                self._populate_implicit_positional(param_name, param_type)
            # f(param = <default>)
            else:
                if type(param.default) in __BUILTIN_TYPES__:
                    self._populate_implicit_option(param_name, param_type)
                elif isinstance(param.default, _TermkitArgument):
                    param.default._populate(self.parser, param_name)

        # f(param : <annotation> (= <default>))
        else:
            # f(param : <annotation>)
            if param.default is inspect.Parameter.empty:
                if param.annotation in __BUILTIN_TYPES__:
                    self._populate_implicit_positional(param_name, param_type)
                elif isinstance(param.annotation, _TermkitArgument):
                    raise SyntaxError("Termkit argument cannot be set from annotation")

            # f(param : <annotation> = <default>)
            else:
                if param.annotation in __BUILTIN_TYPES__:
                    self._populate_implicit_option(param_name, param_type)
                elif isinstance(param.annotation, _TermkitArgument):
                    raise SyntaxError("Termkit argument cannot be set from annotation")
                elif isinstance(param.default, _TermkitArgument):
                    param.default._populate(self.parser, param_name)

    def _populate_implicit_positional(self, param_name: str, param_type: type):
        self.parser.add_argument(param_name, type=param_type)

    def _populate_implicit_option(self, param_name: str, param_type: type):
        param = self.parameters.get(param_name)
        self.parser.add_argument(f"--{param_name}", type=param_type, default=param.default)

    def _get_parameter_type(self, param_name: str):
        param = self.parameters.get(param_name)

        # f(param (= ...))
        if param.annotation is inspect.Parameter.empty:
            # f(param)
            if param.default is inspect.Parameter.empty:
                return str
            # f(param = <default>)
            else:
                if type(param.default) in __BUILTIN_TYPES__:
                    return type(param.default)
                elif isinstance(param.default, _TermkitArgument):
                    return param.default.type

        # f(param : <annotation> (= ...))
        else:
            # f(param : <annotation>)
            if param.default is inspect.Parameter.empty:
                if param.annotation in __BUILTIN_TYPES__:
                    return param.annotation
                elif isinstance(param.annotation, _TermkitArgument):
                    raise SyntaxError("Termkit argument cannot be set from annotation")

            # f(param : <annotation> = <default>)
            else:
                if param.annotation in __BUILTIN_TYPES__:
                    return param.annotation
                elif isinstance(param.annotation, _TermkitArgument):
                    raise SyntaxError("Termkit argument cannot be set from annotation")
