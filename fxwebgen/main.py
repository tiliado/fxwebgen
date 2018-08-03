# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import json
from argparse import ArgumentParser
from typing import List

from fxwebgen.postprocessor import PostProcessor
from fxwebgen.templater import create_templater
from fxwebgen.generator import Generator
from fxwebgen.config import Config


def main(argv: List[str]) -> int:
    config = parse_args(argv)
    print(config)
    if config.global_vars:
        with open(config.global_vars) as fh:
            global_vars = json.load(fh)
    else:
        global_vars = {}
    assert config.templates and config.output_dir
    templater = create_templater(config.templates, global_vars)
    generator = Generator(templater, config.output_dir,
                          pages_dir=config.pages,
                          static_dirs=config.static,
                          post_processor=PostProcessor(global_vars.get('interlinks')))
    generator.build()
    return 0


def parse_args(argv: List[str]) -> Config:
    parser = ArgumentParser(prog=argv[0])
    config = Config()
    config.add_arguments(parser)
    config.set_arguments(parser.parse_args(argv[1:]))
    return config
