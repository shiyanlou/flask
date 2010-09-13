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

.. _Logbook: http://logbook.pocoo.org/
