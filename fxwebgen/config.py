# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import json
import os
from argparse import ArgumentParser, Namespace
from pprint import pprint
from typing import Any, Optional, List

from fxwebgen import yaml
from fxwebgen.context import Context
from fxwebgen.templater import create_templater
from fxwebgen.utils import abspath


class Option:
    def __init__(self, name: str, shortcut: Optional[str], description: str, default: Any,
                 *, required: bool = True, many: bool = False, is_bool: bool = False) -> None:
        self.is_bool = is_bool
        self.required = required
        self.many = many
        self.shortcut = shortcut
        self.name = name
        self.description = description
        self.default = default


OPT_CONFIG = 'config'
OPT_INPUT_DIR = 'input_dir'
OPT_OUTPUT_DIR = 'output_dir'
OPT_GLOBAL_VARS = 'global_vars'
OPT_TEMPLATES_DIR = 'templates_dir'
OPT_STATIC_DIRS = 'static_dirs'
OPT_PAGES_DIR = 'pages_dir'
OPT_TEMPLATE = 'template'
OPT_PATH_PREFIX = 'path_prefix'
OPT_ENABLE_SNIPPETS = 'enable_snippets'
OPT_DOWNGRADE_HEADINGS = 'downgrade_headings'
OPT_TITLE_AS_HEADING = 'title_as_heading'

OPTIONS = {opt.name: opt for opt in (
    Option(OPT_CONFIG, 'c', 'Path to config file [{default}].', 'config.yaml'),
    Option(OPT_INPUT_DIR, 'i', 'Path to input/root directory [{default}].', '.'),
    Option(OPT_OUTPUT_DIR, 'o', 'Path to output directory [{default}].', 'build', required=False),
    Option(OPT_GLOBAL_VARS, 'g', 'Path to global template variables [{default}].', 'data/globals.json', required=False),
    Option(OPT_PAGES_DIR, 'p', 'Path to a directory with pages [{default}].', 'pages'),
    Option(OPT_TEMPLATES_DIR, 't', 'Path to templates directory [].', 'templates'),
    Option(OPT_STATIC_DIRS, 's', 'Path to static files directories.', ['static'], required=False, many=True),
    Option(OPT_TEMPLATE, '', 'The default template name [{default}].', 'page', required=False),
    Option(OPT_PATH_PREFIX, '', 'The prefix to add to the website path[{default}].', '', required=False),
    Option(OPT_ENABLE_SNIPPETS, '', 'Enable or disable snippets [{default}].', True, required=False, is_bool=True),
    Option(OPT_DOWNGRADE_HEADINGS, '', 'Decrease the level of all headings [{default}].',
           False, required=False, is_bool=True),
    Option(OPT_TITLE_AS_HEADING, '', 'Use title as a fallback heading [{default}].',
           False, required=False, is_bool=True),
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

        kwargs: dict = {'dest': option.name}
        if option.many:
            kwargs['nargs'] = '*'
        if option.is_bool:
            kwargs['type'] = _parse_bool
            default = 'yes' if option.default else 'no'
        else:
            default = option.default
        kwargs['help'] = option.description.format(default=default)
        parser.add_argument(*args, **kwargs)


def parse(args: Namespace) -> Context:
    config: Any = None
    # We have input directory as the base path
    if args.input_dir:
        input_dir = abspath(None, args.input_dir)
        # Let's look for config file relative to input dir
        if args.config:
            config = yaml.load_path(abspath(input_dir, args.config))
        else:
            path = abspath(input_dir, OPTIONS[OPT_INPUT_DIR].default)
            if os.path.isfile(path):
                config = yaml.load_path(path)
    # We don't have input directory, but we have config file as a reference path
    elif args.config:
        path = abspath(None, args.config)
        config = yaml.load_path(path)
        input_dir = os.path.dirname(path)
    # Default
    else:
        input_dir = abspath(None, OPTIONS[OPT_INPUT_DIR].default)

    if not config:
        config = {}
    assert isinstance(config, dict), f'Configuration must be a dictionary, not {type(config)}.'
    pprint(config)

    output_dir = _get_path(input_dir, args, config, OPT_OUTPUT_DIR)
    pages_dir = _get_path(input_dir, args, config, OPT_PAGES_DIR, ensure_dir=True)
    templates_dir = _get_path(input_dir, args, config, OPT_TEMPLATES_DIR, ensure_dir=True)
    global_vars_file = _get_path(input_dir, args, config, OPT_GLOBAL_VARS, ensure_file=True, silent=True)
    static_dirs = _get_paths(input_dir, args, config, OPT_STATIC_DIRS, merge=True)
    enable_snippets = _get_bool(args, config, OPT_ENABLE_SNIPPETS)
    downgrade_headings = _get_bool(args, config, OPT_DOWNGRADE_HEADINGS)
    title_as_heading = _get_bool(args, config, OPT_TITLE_AS_HEADING)
    template = _get_string(args, config, OPT_TEMPLATE)
    path_prefix = _get_string(args, config, OPT_PATH_PREFIX)

    assert templates_dir and pages_dir and output_dir
    if global_vars_file:
        with open(global_vars_file) as fh:
            global_vars = json.load(fh)
    else:
        global_vars = {}
    try:
        global_vars.update(config['variables'])
    except KeyError:
        pass

    interlinks = global_vars.get('interlinks', {})
    interlinks.update(config.get('interlinks', {}))

    templater = create_templater(templates_dir, global_vars)
    return Context(templater, output_dir,
                   pages_dir=pages_dir,
                   static_dirs=static_dirs,
                   interlinks=interlinks,
                   enable_snippets=enable_snippets,
                   default_template=template,
                   downgrade_headings=downgrade_headings,
                   title_as_heading=title_as_heading,
                   global_vars=global_vars,
                   path_prefix=path_prefix)


def _get_path(base_path: Optional[str], args: Namespace, config: dict, name: str, *, silent: bool = False,
              ensure_dir: bool = False, ensure_file: bool = False) -> Optional[str]:
    value = getattr(args, name)
    if value is None:
        value = config.get(name)
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


def _get_paths(base_path: Optional[str], args: Namespace, config: dict, name: str,
               *, silent: bool = False, merge: bool = False) -> List[str]:
    args_values: List[str] = getattr(args, name, None)
    config_values = config.get(name)
    if config_values is not None and not isinstance(config_values, list):
        config_values = [config_values]
    if args_values is None and config_values is None:
        values: Optional[List[str]] = None
    elif args_values is None:
        values = config_values
    elif config_values is None:
        values = args_values
    elif merge:
        values = args_values + config_values
    else:
        values = args_values or config_values

    option = OPTIONS[name]
    if values is not None:
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


def _parse_bool(value: Optional[str]) -> Optional[bool]:
    return None if value is None else (value.strip().lower() in ('yes', 'true', 'on'))


def _get_bool(args: Namespace, config: dict, name: str) -> bool:
    value = getattr(args, name, None)
    if value is None:
        value = config.get(name)
        if isinstance(value, str):
            value = _parse_bool(value)
    if value is None:
        value = OPTIONS[name].default
    assert isinstance(value, bool), f'Unexpected type instead of bool: {type(value)}.'
    return value


def _get_string(args: Namespace, config: dict, name: str) -> str:
    value = getattr(args, name, None)
    if value is None:
        value = config.get(name)
    if value is None:
        value = OPTIONS[name].default
    assert isinstance(value, str), f'Unexpected type instead of string: {type(value)}.'
    return value


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
