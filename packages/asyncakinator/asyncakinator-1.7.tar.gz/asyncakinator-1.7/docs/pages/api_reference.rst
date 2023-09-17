.. py:currentmodule:: asyncakinator


API Reference
=============

Akinator
--------
.. autoclass:: Akinator
    :members:

Models
------
.. autoclass:: Answer
    :members:

.. autoclass:: Language
    :members:

.. autoclass:: Theme
    :members:

.. autoclass:: Guess
    :exclude-members: id, name, probablility, description, ranking, absolute_picture_path
    :members:

Utils
-----

MISSING
~~~~~~~
.. attribute:: akinator.utils.MISSING

A sentinel value that is used to indicate a missing value with distinction from :class:`None`.


Exceptions
----------

.. autoclass:: InputError
    :members:

.. autoclass:: InvalidAnswer
    :members:

.. autoclass:: InvalidLanguage
    :members:

.. autoclass:: InvalidTheme
    :members:

.. autoclass:: ConnectionFailure
    :members:

.. autoclass:: TimedOut
    :members:

.. autoclass:: NoMoreQuestions
    :members:

.. autoclass:: ServerDown
    :members:

.. autoclass:: TechnicalServerError
    :members:

.. autoclass:: NotStarted
    :members:

.. autoclass:: CanNotGoBack
    :members: