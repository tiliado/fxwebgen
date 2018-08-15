#!/usr/bin/env python3.6
# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.

if __name__ == '__main__':
    import os
    import sys
    fxwebgen_dir = os.path.abspath('fxwebgen')
    if os.path.isfile(os.path.join(fxwebgen_dir, '__init__.py')):
        sys.path.append(fxwebgen_dir)
    from fxwebgen.main import run
    run()
