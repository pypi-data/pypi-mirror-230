"""
Copyright 2023, Thomas Mahé <contact@tmahe.dev>
SPDX-License-Identifier: MIT
"""

import argparse
import inspect
import typing

__RESERVED_PREFIXES__ = ["_TERMKIT_"]


def filter_args(ns: argparse.Namespace, callback: typing.Callable) -> typing.Dict:
    out = ns.__dict__.copy()
    params = inspect.signature(callback).parameters.keys()
    for arg in ns.__dict__.keys():
        for reserved_prefix in __RESERVED_PREFIXES__:
            if reserved_prefix in arg or arg not in params:
                del out[arg]
    return out
