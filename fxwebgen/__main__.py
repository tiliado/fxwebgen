# Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>
# Licensed under BSD-2-Clause license - see file LICENSE for details.


def run() -> None:
    import sys
    from fxwebgen.main import main

    # noinspection PyBroadException
    try:
        code = main(sys.argv)
    except Exception:  # pylint: disable=broad-except
        import traceback
        print("Unexpected failure:", file=sys.stderr)
        traceback.print_exc()
        code = 2
    sys.exit(code)


if __name__ == "__main__":
    run()
