# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import json
import os
from argparse import ArgumentParser, Namespace
from typing import Any, Optional, List

from fxwebgen.context import Context
from fxwebgen.templater import create_templater


class Option:
    def __init__(self, name: str, shortcut: Optional[str], description: str, default: Any,
                 *, required: bool = True, many: bool = False) -> None:
        self.required = required
        self.many = many
        self.shortcut = shortcut
        self.name = name
        self.description = description
        self.default = default


OPT_INPUT_DIR = 'input_dir'
OPT_OUTPUT_DIR = 'output_dir'
OPT_GLOBAL_VARS = 'global_vars'
OPT_TEMPLATES_DIR = 'templates_dir'
OPT_STATIC_DIRS = 'static_dir'
OPT_PAGES_DIR = 'pages_dir'

OPTIONS = {opt.name: opt for opt in (
    Option(OPT_INPUT_DIR, 'i', 'Path to input/root directory [{default}].', '.'),
    Option(OPT_OUTPUT_DIR, 'o', 'Path to output directory [{default}].', 'build', required=False),
    Option(OPT_GLOBAL_VARS, 'g', 'Path to global template variables [{default}].', 'data/globals.json', required=False),
    Option(OPT_PAGES_DIR, 'p', 'Path to a directory with pages [{default}].', 'pages'),
    Option(OPT_TEMPLATES_DIR, 't', 'Path to templates directory [].', 'templates'),
    Option(OPT_STATIC_DIRS, 's', 'Path to static files directories.', ['static'], required=False, many=True),
)}


def add_arguments(parser: ArgumentParser) -> None:
    for option in OPTIONS.values():
        args = []
        if option.shortcut:
            args.append('-' + option.shortcut)
        long = '--' + option.name.replace('_', '-')
        if option.many and long.endswith('s'):
            long = long[:-1]
        args.append(long)
        kwargs = {
            'help': option.description.format(default=option.default),
            'dest': option.name,
        }
        if option.many:
            kwargs['nargs'] = '*'
        parser.add_argument(*args, **kwargs)  # type: ignore


def parse(args: Namespace) -> Context:
    input_dir = abspath(None, args.input_dir or OPTIONS[OPT_INPUT_DIR].default)
    output_dir = _get_path(input_dir, args, OPT_OUTPUT_DIR)
    pages_dir = _get_path(input_dir, args, OPT_PAGES_DIR, ensure_dir=True)
    templates_dir = _get_path(input_dir, args, OPT_TEMPLATES_DIR, ensure_dir=True)
    global_vars_file = _get_path(input_dir, args, OPT_GLOBAL_VARS, ensure_file=True, silent=True)
    static_dirs = _get_paths(input_dir, args, OPT_STATIC_DIRS)

    assert templates_dir and pages_dir and output_dir
    if global_vars_file:
        with open(global_vars_file) as fh:
            global_vars = json.load(fh)
    else:
        global_vars = {}

    templater = create_templater(templates_dir, global_vars)
    return Context(templater, output_dir,
                   pages_dir=pages_dir,
                   static_dirs=static_dirs,
                   interlinks=global_vars.get('interlinks'))


def _get_path(base_path: Optional[str], args: Namespace, name: str, *, silent: bool = False,
              ensure_dir: bool = False, ensure_file: bool = False) -> Optional[str]:
    value = getattr(args, name)
    option = OPTIONS[name]
    if value:
        path = abspath(base_path, value)
        silent = False
    else:
        path = abspath(base_path, option.default)
    try:
        if ensure_dir:
            assert path and os.path.isdir(path), \
                f'{name}: Directory "{path}" does not exist.'
        elif ensure_file:
            assert path and os.path.isfile(path), \
                f'{name}: File "{path}" does not exist.'
        return path.rstrip('/')
    except AssertionError as e:
        if option.required:
            raise
        elif not silent:
            print(e)
    return None


def _get_paths(base_path: Optional[str], args: Namespace, name: str, silent: bool = False) -> List[str]:
    values = getattr(args, name)
    option = OPTIONS[name]
    if values:
        return _check_dirs([abspath(base_path, value) for value in values])
    else:
        try:
            return _check_dirs([abspath(base_path, value) for value in option.default])
        except AssertionError as e:
            if option.required:
                raise
            elif not silent:
                print(e)
    return []


def abspath(base_path: Optional[str], path: str) -> str:
    assert path, f'Path must be specified.'
    assert base_path is None or os.path.isabs(base_path), f'Base path "{base_path}" is not absolute.'
    if os.path.isabs(path):
        return path
    return os.path.join(base_path, path) if base_path else os.path.abspath(path)


def _check_dirs(dirs: List[str]) -> List[str]:
    valid_dirs = []
    for path in dirs:
        if path:
            path = path.rstrip('/')
            if os.path.isdir(path):
                valid_dirs.append(path)
            else:
                raise AssertionError(f'Directory "{path}" does not exist.')
    return valid_dirs
