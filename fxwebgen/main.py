# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import os
from argparse import ArgumentParser
from threading import Thread
from typing import List

from fxwebgen.postprocessor import PostProcessor
from fxwebgen.generator import Generator
from fxwebgen import config
from fxwebgen.server import create_server


def main(argv: List[str]) -> int:
    parser = ArgumentParser(prog=argv[0])
    config.add_arguments(parser)
    parser.add_argument('--serve', action='store_true', help='Start a HTTP server for the output directory')
    args = parser.parse_args(argv[1:])
    ctx = config.parse(args)
    generator = Generator(ctx, post_processor=PostProcessor())
    generator.build()
    if args.serve:
        os.chdir(ctx.output_dir)
        server = create_server()
        thread = Thread(target=server.serve_forever)
        thread.daemon = True
        while True:
            command = input('[R]egenerate [Q]uit ? ').strip().upper()
            if command == 'R':
                generator.build()
            elif command == 'Q':
                break
            elif command:
                print(f'Unknown command: "{command}".')
    return 0
