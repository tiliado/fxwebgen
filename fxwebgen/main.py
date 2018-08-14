# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

import os
from argparse import ArgumentParser
from multiprocessing import Process
from typing import List

from fxwebgen.utils import SmartFormatter
from fxwebgen.postprocessor import PostProcessor
from fxwebgen.generator import Generator, FORCE_REBUILD_CHOICES, FORCE_PAGES, FORCE_TEMPLATE
from fxwebgen import config
from fxwebgen.server import create_server


def main(argv: List[str]) -> int:
    parser = ArgumentParser(
        prog=argv[0],
        formatter_class=SmartFormatter,
        description='About\n=====\n\n'
                    'Generate static website from Markdown and HTML sources and Jinja2 templates.\n\n'
                    'Unless otherwise noted, all commandline options can be used in a configuration file '
                    'in the YAML format (see --config option).'
                    '\n\nArguments\n=========\n\n')
    config.add_arguments(parser)
    parser.add_argument('--serve', action='store_true',
                        help='Start a HTTP server for the output directory. This option is not read from a '
                             'configuration file. Note that when "path_prefix" is specified, the website is exported '
                             'at the path prefix under the output directory.')
    parser.add_argument('-f', '--force', nargs='+', choices=FORCE_REBUILD_CHOICES,
                        help='Select what component to regenerate even though they seem to be unmodified. '
                             'This option is not read from a configuration file.')
    args = parser.parse_args(argv[1:])
    ctx = config.parse(args)
    generator = Generator(ctx, post_processor=PostProcessor())
    generator.build(force=args.force)
    if args.serve:
        def serve() -> None:
            os.chdir(ctx.output_root)
            server = create_server()
            server.serve_forever()
        process = Process(target=serve)
        process.daemon = True
        process.start()
        try:
            while True:
                # noinspection SpellCheckingInspection
                command = input('[R]egenerate [Q]uit | Force rebuild: [P]ages, [T]emplate: ').strip().upper()
                if command == 'P':
                    generator.build(force=[FORCE_PAGES])
                elif command == 'T':
                    generator.build(force=[FORCE_TEMPLATE])
                elif command in ('R', ''):
                    generator.build()
                elif command == 'Q':
                    break
                elif command:
                    print(f'Unknown command: "{command}".')
        finally:
            process.terminate()
    return 0
