# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import os
from argparse import ArgumentParser
from multiprocessing import Process
from typing import List

from fxwebgen.postprocessor import PostProcessor
from fxwebgen.generator import Generator
from fxwebgen import config
from fxwebgen.server import create_server


def main(argv: List[str]) -> int:
    parser = ArgumentParser(prog=argv[0])
    config.add_arguments(parser)
    parser.add_argument('--serve', action='store_true', help='Start a HTTP server for the output directory')
    parser.add_argument('-f', '--force', action='store_true', help='Force rebuild all.')
    args = parser.parse_args(argv[1:])
    ctx = config.parse(args)
    generator = Generator(ctx, post_processor=PostProcessor())
    if args.force:
        generator.purge()
    generator.build()
    if args.serve:
        def serve() -> None:
            os.chdir(ctx.output_dir)
            server = create_server()
            server.serve_forever()
        process = Process(target=serve)
        process.daemon = True
        process.start()
        try:
            while True:
                command = input('[R]egenerate [Q]uit ? ').strip().upper()
                if command == 'R':
                    generator.build()
                elif command == 'Q':
                    break
                elif command:
                    print(f'Unknown command: "{command}".')
        finally:
            process.terminate()
    return 0
