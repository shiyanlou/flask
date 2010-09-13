# -*- coding: utf-8 -*-
"""
    flask.logging
    ~~~~~~~~~~~~~

    Implements the logging support for Flask.  This is not supposed to be a
    abstraction layer above multiple logging systems, it mainly exists because
    Flask started out using logging and is currently in the process to switch
    to Logbook.  This module will become mostly useless once we drop support
    for the stdlib's logging.

    In some other parts of Flask there are explicit hardcoded checks that
    opt-in features in case Logbook is present.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import


def create_logger(app):
    """Creates a new logger for the application.  This is mainly needed
    because Flask supports dynamic logger name changes.  Once we drop
    support for logging we can remove this as well because it is easily
    possible to reflect the channel name from another value in logbook
    """
    return logging_systems[app.logging_system][1](app)


def init_logging_system(app):
    """Initializes the logging system for this app."""
    return logging_systems[app.logging_system][0](app)


def create_logbook_logger(app):
    """Initializes the logbook default config for the application."""
    from logbook import Logger
    return Logger(app.logger_name)


def init_logbook(app):
    """Stuffs a default logging setup on the application object in case
    the attribute was not set so far.
    """
    if app.logbook_setup is None:
        from logbook import StderrHandler
        app.logbook_setup = StderrHandler(format_string=(
            '-' * 80 + '\n' +
            '{record.level_name} in {record.module} '
                '[{record.filename}:{record.lineno}]:\n' +
            '{record.message}\n' +
            '-' * 80
        ))


def create_logging_logger(app):
    """Creates a logger for the given application.  This logger works
    similar to a regular Python logger but changes the effective logging
    level based on the application's debug flag.  Furthermore this
    function also removes all attached handlers in case there was a
    logger with the log name before.
    """
    from logging import getLogger, StreamHandler, Formatter, Logger, DEBUG

    class DebugLogger(Logger):
        def getEffectiveLevel(x):
            return DEBUG if app.debug else Logger.getEffectiveLevel(x)

    class DebugHandler(StreamHandler):
        def emit(x, record):
            StreamHandler.emit(x, record) if app.debug else None

    handler = DebugHandler()
    handler.setLevel(DEBUG)
    handler.setFormatter(Formatter(
        '-' * 80 + '\n' +
        '%(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n' +
        '%(message)s\n' +
        '-' * 80
    ))
    logger = getLogger(app.logger_name)
    # just in case that was not a new logger, get rid of all the handlers
    # already attached to it.
    del logger.handlers[:]
    logger.__class__ = DebugLogger
    logger.addHandler(handler)
    return logger


def create_dummy_logger(app):
    """Creates a dummy logger."""
    return _DummyLogger(app.logger_name)


class _DummyLogger(object):
    """Not a very helpful logger."""
    def __init__(self, name, level=0):
        self.name = name
        self.level = level
    debug = info = warn = warning = notice = error = exception = \
        critical = log = lambda *a, **kw: None


_dummy = lambda x: None
logging_systems = {
    'logbook':      (init_logbook, create_logbook_logger),
    'logging':      (_dummy, create_logging_logger),
    'none':         (_dummy, create_dummy_logger)
}
