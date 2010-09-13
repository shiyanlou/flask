.. _logging:

Logging and Errorhandling
=========================

.. versionadded:: 0.7

Applications fail, servers fail.  Sooner or later you will see an exception
in production.  Even if your code is 100% correct, you will still see
exceptions from time to time.  Why?  Because everything else involved will
fail.  Here some situations where perfectly fine code can lead to server
errors:

-   the client terminated the request early and the application was still
    reading from the incoming data.
-   the database server was overloaded and could not handle the query.
-   a filesystem is full
-   a harddrive crashed
-   a backend server overloaded
-   a programming error in a library you are using
-   network connection of the server to another system failed.

And that's just a small sample of issues you could be facing.  So how do we
deal with that sort of problem?  By default if your application runs in
production mode, Flask will display a very simple page for you and log the
exception to the :attr:`~flask.Flask.logger`.

But there is more you can do, and we will cover some better setups to deal
with errors.

The Logging System
------------------

In Flask 0.3 we started off with supporting a clever default configuration
of the :mod:`logging` package that comes with Python.  In Flask 0.7 we are
starting to make the switch to a new log system called `Logbook`_.

The default will continue to be the logging module until we hit 1.0 when
we change the default to Logbook.  Two versions after that we will remove
the support for logging in general.

Why are we doing that?  Unfortunately the logging library in Python was
designed with a different kind of application setup in mind.  In web
applications what happens is that a thread usually handles a request and
whatever is happening in this thread until a certain point is considered
"belonging" to the same request.  The Python logging library however does
not support the idea of per-thread based configurations.  Instead it is
using a global registry of loggers which does not translate well to an
application setup.

The way logbook works is that it keeps per-thread configurations of your
logging system which gives you the ability to better customize the
behaviour of the system and provides better means of debugging.

This document only specifies a logbook setup.  If you are interested in
the documentation for the old logging system, have a look at
:ref:`old-logging`.

Making the Switch
-----------------

The default configuration of Logbook is fine and Flask even adds a small
little improvement on top of that.  However you currently have to opt-in
for Logbook support::

    from flask import Flask
    app = Flask(__name__, logging_system='logbook')

The other options for the logging system are:

``'logging'``
    Deprecated support for logging to the logging system.

``'logbook'``
    Logging to `Logbook`_, requires that the library is installed.

``'none'``
    Configure a dummy logger for internal usage but do not set up a
    real logging system.

In Flask 1.0 the logging system parameter will become a no-op and Logbook
will always be used.  In case Logbook is not installed in 1.0 and later,
it will dynamically fall back to the dummy logger which currently is not
the case.

Logging Messages
----------------

If you have used logging before in Flask applications you will have used
the :attr:`~flask.Flask.logger` attribute.  While that is nice and you can
continue to use this logger, it is recommended to use a logger for logging
directly.  The reason for this is that you have better control over what
you are doing and can shut down a logger completely to reduce runtime
overhead.

To make the switch, replace calls to this::

    @app.route('/')
    def index():
        app.logger.warn('A message')
        ...

With something like this::

    from logbook import Logger
    logger = Logger('My component')

    @app.route('/')
    def index():
        logger.warn('A message')
        ...

Note that Logbook is using Python 2.6's new string formatting feature
instead of the printf style string formatting that was in use by logging::

    app.logger.warn('Hello %s!', name)

Becomes this now::

    app.logger.warn('Hello {0}!', name)

You can also use named parameters::

    app.logger.warn('Hello {name}!', name=name)

Logbook ships with a pure Python implementation of the new string
formatting for Python 2.5 which is why it is recommended to use Python 2.6
in case you are doing a lot of logging calls that are delivered to
handlers in production.  It will of course not affect logging calls that
don't happen because their level is too low (like debug log calls on a
production system that only cares about warnings and higher priority
records).

Consult the `Logbook documentation`_ for more information.

Error Mails
-----------

If the application runs in production mode (which it will do on your
server) you won't see any log messages by default.  Why is that?  Flask
tries to be a zero-configuration framework.  Where should it drop the logs
for you if there is no configuration?  Guessing is not a good idea because
chances are, the place it guessed is not the place where the user has
permission to create a logfile.  Also, for most small applications nobody
will look at the logs anyways.

In fact, I promise you right now that if you configure a logfile for the
application errors you will never look at it except for debugging an issue
when a user reported it for you.  What you want instead is a mail the
second the exception happened.  Then you get an alert and you can do
something about it.

Flask uses the Python builtin logging system, and it can actually send
you mails for errors which is probably what you want.  Here is how you can
configure the Flask logger to send you mails for exceptions::

    ADMINS = ['yourname@example.com']
    if not app.debug:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler('127.0.0.1',
                                   'server-error@example.com',
                                   ADMINS, 'YourApplication Failed')
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

So what just happened?  We created a new
:class:`~logging.handlers.SMTPHandler` that will send mails with the mail
server listening on ``127.0.0.1`` to all the `ADMINS` from the address
*server-error@example.com* with the subject "YourApplication Failed".  If
your mail server requires credentials, these can also be provided.  For
that check out the documentation for the
:class:`~logging.handlers.SMTPHandler`.

We also tell the handler to only send errors and more critical messages.
Because we certainly don't want to get a mail for warnings or other
useless logs that might happen during request handling.

Before you run that in production, please also look at :ref:`logformat` to
put more information into that error mail.  That will save you from a lot
of frustration.


.. _Logbook: http://logbook.pocoo.org/
.. _Logbook documentation: http://logbook.pocoo.org/
