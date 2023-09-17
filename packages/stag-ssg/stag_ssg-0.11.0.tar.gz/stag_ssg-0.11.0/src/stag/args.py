import argparse
import functools


class ArgumentParser:
    def __init__(self, *a, **kw):
        self._parser = argparse.ArgumentParser(*a, **kw)
        self._subparsers = None
        self._subpmap = {}

    @property
    def parser(self):
        return self._parser

    def parse_args(self, *a, **kw):
        return self.parser.parse_args(*a, **kw)

    def subcommand(self, name=None):
        """Decorator for subcommands. Decorated function will be available as a
        subcommand, which is available via args.func. For example:

            cli = args.ArgumentParser()

            @cli.subcommand()
            def mycommand():
                pass

            args = parse_args()
            args.func()
        """

        def _deco(fn):
            if not self._subparsers:
                self._subparsers = self.parser.add_subparsers()

            subpname = name if name else fn.__name__
            parser = self._subparsers.add_parser(subpname, description=fn.__doc__)
            parser.set_defaults(func=fn)
            self._subpmap[fn] = parser
            return fn

        return _deco

    def arg(self, *a, **kw):
        """Decorator to add arguments to a subcommand:

        @cli.arg("foo", default=42, help="some help")
        @cli.subcommand()
        def mycommand():
            pass
        """

        def _deco(fn):
            subp = self._subpmap[fn]
            subp.add_argument(*a, **kw)
            return fn

        return _deco
