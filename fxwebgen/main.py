# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

from argparse import ArgumentParser
from typing import List

from fxwebgen.postprocessor import PostProcessor
from fxwebgen.generator import Generator
from fxwebgen import config


def main(argv: List[str]) -> int:
    parser = ArgumentParser(prog=argv[0])
    config.add_arguments(parser)
    ctx = config.parse(parser.parse_args(argv[1:]))
    generator = Generator(ctx, post_processor=PostProcessor())
    generator.build()
    return 0
