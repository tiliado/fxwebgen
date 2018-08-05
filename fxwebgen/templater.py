# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import json
import os
from typing import Dict, Any, Union, List, Tuple, Iterable, Mapping, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template, TemplateError


def to_dict(value: Iterable[Mapping], key: Any) -> Dict[Any, Mapping]:
    return {item[key]: item for item in value or []}


def create_templater(template_dir: str, global_vars: Optional[Dict[str, Any]] = None) -> "Templater":
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    if global_vars:
        env.globals.update(global_vars)
    env.filters['todict'] = to_dict
    return Templater(template_dir, env)


class Templater:
    env: Environment
    templates: Dict[str, Tuple[Template, dict]]

    def __init__(self, template_dir: str, env: Environment) -> None:
        self.template_dir = template_dir
        self.env = env
        self.templates = {}

    def clear_cache(self) -> None:
        self.templates.clear()

    def load_template_data(self, name: str) -> dict:
        path = os.path.join(self.template_dir, os.path.splitext(name)[0] + '.json')
        if os.path.isfile(path):
            with open(path) as fh:
                data: dict = json.load(fh)
                return data
        return {}

    # pylint: disable=inconsistent-return-statements
    def get_template(self, name: Union[str, List[str]]) -> Tuple[Template, dict]:
        if isinstance(name, str):
            try:
                return self.templates[name]
            except KeyError:
                template = self.env.get_template(name)
                data = self.load_template_data(name)
                result = template, data
                self.templates[name] = result
                return result
        elif not name:
            raise ValueError("Template list must not be empty")
        else:
            errors = []
            for item in name:
                try:
                    return self.get_template(item)
                except TemplateError as e:
                    errors.append(e)
            raise ValueError(errors)

    def render(self, name: Union[str, List[str]], variables: Dict[str, Any]) -> str:
        template, data = self.get_template(name)
        variables['data'] = data
        result = template.render(**variables)
        del variables['data']
        return result
