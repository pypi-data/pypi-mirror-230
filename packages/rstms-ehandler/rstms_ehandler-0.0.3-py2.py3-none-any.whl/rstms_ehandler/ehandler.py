"""
  ehandler

  well-behaved exception handler for python cli commands

"""

import sys
from traceback import format_exception


def exception_handler(
    exception_type,
    exception,
    traceback,
    debug_hook=sys.excepthook,
):
    if ExceptionHandler.pdb:
        import pdb

        pdb.post_mortem(traceback)

    logger = ExceptionHandler.logger

    elist = format_exception(exception)
    traceback_msg = "".join(elist[:-1]).rstrip("\n")
    error_msg = elist[-1].rstrip("\n")

    if logger:
        logger.debug(traceback_msg)
        logger.error(error_msg)

    if ExceptionHandler.debug:
        debug_hook(
            exception_type,
            exception,
            traceback,
        )
    elif not logger:
        print(error_msg, file=sys.stderr, end="\n", flush=True)

    sys.exit(-1)


class ExceptionHandler:
    installed = False
    debug = False
    pdb = False
    logger = None

    def __init__(self, **kwargs):
        """initialize ExceptionHandler with optional kwargs:
        ctx=None        initialize click ctx.obj and set 'ehandler'
        debug=False     output full stack trace
        logger=None     log exceptions to logger
        pdb=False       break into postmortem debugger
        """
        self.__class__.debug = kwargs.setdefault("debug", self.debug)
        self.__class__.logger = kwargs.setdefault("logger", self.logger)
        self.__class__.pdb = kwargs.setdefault("pdb", self.pdb)
        if not self.installed:
            sys.excepthook = exception_handler
            self.__class__.installed = True
        if "ctx" in kwargs:
            ctx = kwargs["ctx"]
            if ctx.obj is None:
                ctx.obj = {}
            ctx.obj["ehandler"] = self
            ctx.obj["debug"] = self.debug
            ctx.obj["logger"] = self.logger
            ctx.obj["pdb"] = self.pdb

    def __repr__(self):
        return (
            super().__repr__()
            + f"(debug={self.debug}, logger={self.logger}, pdb={self.pdb})"
        )


def set_ehandler_option(ctx=None, option=None, value=None, **kwargs):
    kwargs = dict(ctx=ctx)
    kwargs[option.name] = value
    ExceptionHandler(**kwargs)
    return value
