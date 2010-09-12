# -*- coding: utf-8 -*-
"""
    flask.logging
    ~~~~~~~~~~~~~

    Implements the logging support for Flask.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import


def create_logger(app):
    """Initializes the logging system for this app."""
    return logging_systems[app.logging_system](app)


def init_logbook(app):
    """Initializes the logbook default config for the application."""
    try:
        from logbook import Logger
    except ImportError:
        raise RuntimeError('Logbook is not installed but required for '
                           'the logbook logging backend.')
    return Logger(app.logger_name)


def init_logging(app):
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
    handler.setFormatter(Formatter(app.debug_log_format))
    logger = getLogger(app.logger_name)
    # just in case that was not a new logger, get rid of all the handlers
    # already attached to it.
    del logger.handlers[:]
    logger.__class__ = DebugLogger
    logger.addHandler(handler)
    return logger


logging_systems = {
    'logbook':      init_logbook,
    'logging':      init_logging
}
