"""
Copyright 2023, Thomas Mahé <contact@tmahe.dev>
SPDX-License-Identifier: MIT
"""

import argparse
from abc import abstractmethod
from typing import Optional


class _TermkitArgument:
    @abstractmethod
    def _populate(self, parser: argparse.ArgumentParser, dest: str):
        ...

    @property
    def argparse_params(self):
        out = self.__dict__
        for item in ["flags"]:
            if item in out.keys():
                del out[item]
        return out


class Positional(_TermkitArgument):
    def __init__(self, type: Optional[type] = str, help: Optional[str] = None, metavar: Optional[str] = None):
        self.type = type
        self.help = help
        self.metavar = metavar

    def _populate(self, parser: argparse.ArgumentParser, dest: str):
        parser.add_argument(dest, **self.argparse_params)


class Option(_TermkitArgument):
    def __init__(
        self,
        *flags: str,
        type: Optional[type] = str,
        help: Optional[str] = None,
        metavar: Optional[str] = None,
        required: bool = False
    ):
        self.flags = flags
        self.type = type
        self.help = help
        self.metavar = metavar
        self.required = required

    def _populate(self, parser: argparse.ArgumentParser, dest: str):
        parser.add_argument(*self.flags, **self.argparse_params, dest=dest)
