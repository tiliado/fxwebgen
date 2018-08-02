# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import os
from argparse import ArgumentParser, Namespace
from typing import Any, Optional, List, Generic, TypeVar, Dict, cast, Tuple

T = TypeVar('T')


class Option(Generic[T]):
    def __init__(self, shortcut: Optional[str], description: str, default: T,
                 required: bool = True, *, many: bool = False) -> None:
        self.required = required
        self.many = many
        self.shortcut = shortcut
        self.name = ''
        self.description = description
        self.default = default

    def __get__(self, instance: Any, owner: Any) -> Optional[T]:
        return cast(Optional[T], instance.__dict__.get(self.name))

    def __set__(self, instance: Any, value: T) -> None:
        value = self.check(value)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner: Any, name: str) -> None:
        self.name = name

    # pylint: disable=no-self-use
    def check(self, value: T) -> T:
        return value


class Directory(Option[str]):
    # pylint: disable=no-self-use
    def check(self, value: str) -> str:
        return value.rstrip('/')


class Directories(Option[List[str]]):
    # pylint: disable=no-self-use
    def check(self, values: List[str]) -> List[str]:
        valid_values = []
        for value in values:
            if value:
                value = value.rstrip('/')
                if os.path.isdir(value):
                    valid_values.append(value)
                else:
                    raise AssertionError(f'{self.name}: Directory "{value}" does not exist.')
        return valid_values


class File(Option[str]):
    # pylint: disable=no-self-use
    def check(self, value: str) -> str:
        return value.rstrip('/')


class ConfigMeta(type):
    def __new__(mcs, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> type:
        namespace['all_options'] = {name: value for name, value in namespace.items() if isinstance(value, Option)}
        return super(ConfigMeta, mcs).__new__(mcs, name, bases, namespace)


class Config(metaclass=ConfigMeta):
    input_dir = Directory('i', 'Path to input/root directory [{default}].', '.')
    output_dir = Directory('o', 'Path to output directory [{default}].', 'build', False)
    global_vars = File('g', 'Path to global template variables [{default}].', 'data/globals.json', False)
    pages = Directory('p', 'Path to a directory with pages [{default}].', 'pages')
    templates = Directory('t', 'Path to templates directory [].', 'templates')
    static = Directories('s', 'Path to static files directories.', ['static'], False, many=True)
    all_options: Dict[str, Option]

    def add_arguments(self, parser: ArgumentParser) -> None:
        for option in self.all_options.values():
            args = []
            if option.shortcut:
                args.append('-' + option.shortcut)
            args.append('--' + option.name.replace('_', '-'))
            kwargs = {
                'help': option.description.format(default=option.default),
            }
            if option.many:
                kwargs['nargs'] = '*'
            parser.add_argument(*args, **kwargs)  # type: ignore

    def set_arguments(self, args: Namespace) -> None:
        self.input_dir = os.path.abspath(args.input_dir or self.all_options['input_dir'].default)
        self._set_path(args, 'output_dir')
        for name in 'pages', 'templates':
            self._set_path(args, name, ensure_dir=True)
        self._set_path(args, 'global_vars', ensure_file=True, silent=True)
        self._set_paths(args, 'static')

    def _set_path(self, args: Namespace, name: str, *, silent: bool = False,
                  ensure_dir: bool = False, ensure_file: bool = False) -> None:
        value = getattr(args, name)
        option = self.all_options[name]
        if value:
            path = self.abspath(value)
            silent = False
        else:
            path = self.abspath(option.default)
        try:
            if ensure_dir:
                assert path and os.path.isdir(path), \
                    f'{name}: Directory "{path}" does not exist.'
            elif ensure_file:
                assert path and os.path.isfile(path), \
                    f'{name}: File "{path}" does not exist.'
            setattr(self, name, path)
        except AssertionError as e:
            if option.required:
                raise
            elif not silent:
                print(e)

    def _set_paths(self, args: Namespace, name: str, silent: bool = False) -> None:
        values = getattr(args, name)
        option = self.all_options[name]
        if values:
            setattr(self, name, [self.abspath(value) for value in values])
        else:
            try:
                setattr(self, name, [self.abspath(value) for value in option.default])
            except AssertionError as e:
                if option.required:
                    raise
                elif not silent:
                    print(e)

    def abspath(self, path: Optional[str]) -> Optional[str]:
        if not path:
            return None
        assert self.input_dir
        return path if os.path.isabs(path) else os.path.join(self.input_dir, path)

    def __repr__(self) -> str:
        return '[{}]'.format(', '.join(f'{name}: {getattr(self, name)}' for name in self.all_options))
