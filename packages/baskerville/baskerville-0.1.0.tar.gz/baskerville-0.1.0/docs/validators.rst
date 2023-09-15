Validators
==========

Validators take a string and returns whether this string satisfies a set of rules.
The most common application of this is for data types.
Validators also capture state. For example, the ``Integer`` validator keeps track of the largest value it has seen.

Text
----

.. autoclass:: baskerville.Text
    :members:

.. autoclass:: baskerville.Literal
    :members:

Numeric
-------

.. autoclass:: baskerville.Integer
    :members:

.. autoclass:: baskerville.Float
    :members:

Time
----

.. autoclass:: baskerville.Date
    :members:

.. autoclass:: baskerville.Time
    :members:

.. autoclass:: baskerville.DateTime
    :members:

.. autoclass:: baskerville.DateTimeFormat
    :members:
    :undoc-members:

Other
-----

.. autoclass:: baskerville.Empty
    :members:

.. autoclass:: baskerville.Unique
    :members:

