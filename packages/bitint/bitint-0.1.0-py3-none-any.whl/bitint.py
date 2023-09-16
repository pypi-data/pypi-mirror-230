from functools import reduce


def bitint(typename, value_names):
    """Represents set by named bits

    The left-most bit name is represented by first bit (value 1).

    (Inspired by namedtuple.)

    bitint() creates a new type derived from int
    >>> B = bitint('B', ['first', 'second', 'third'])

    The init args for bitint subclasses
    >>> x = B('first')
    >>> isinstance(x, int)
    True
    >>> int(x)
    1

    Bit names (ie. flags) are stored as properties with positional bit value
    >>> x.first
    1
    >>> x.third
    4

    This can be used to efficient test if a bit is set ...
    >>> B.first in x
    True
    >>> B.second in x
    False

    ... or for standard binary operators
    >>> (B.first | B.second) & x
    1

    The presence of a set bit can be dfirst by string literal as well (this
    method is slightly less efficient)
    >>> 'first' in x
    True
    >>> 'second' in x
    False

    Standard binary operations can be used with BitInt
    >>> bool(0b10 & x)
    False
    >>> bool(0b01 & x)
    True

    Finaly, BitInt can be initialized by an integer number as well
    >>> x = B(0b110)
    >>> B.first in x
    False
    >>> B.second in x
    True

    BitInt is iterable returning names of set flags.
    >>> list(x)
    ['second', 'third']

    Bit names and their values are stored in `_bits` property.
    >>> x._bits
    {'first': 1, 'second': 2, 'third': 4}


    Finally string representation of BitInt is vinary field
    >>> str(x)
    '110'

    AND, OR and INVERSE bit operations returns BitInt object
    >>> x | 1
    B('first', 'second', 'third')
    >>> x
    B('second', 'third')
    >>> x & 2
    B('second')
    >>> ~x
    B('first')
    >>> x |=1
    >>> x
    B('first', 'second', 'third')
    >>> x &= 1
    >>> x
    B('first')

    """

    typename = str(typename)
    if isinstance(value_names, str):
        value_names = value_names.replace(',', ' ').split()
    bits = {str(name):1<<index for index, name in enumerate(value_names)}
    names = {1<<index:str(name) for index, name in enumerate(value_names)}

    _int_new = int.__new__
    def __new__(cls, *flags):
        if len(flags) == 1 and isinstance(flags[0], int):
            return _int_new(cls, flags[0])
        return _int_new(cls, reduce(lambda a, b: a | b, (bits[v] for v in flags), 0))

    def _as_set(self):
        return {
            name
            for name, value in self._bits.items()
            if value & self
        }
    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join((repr(_) for _ in self))})'


    def __str__(self):
        return '{0:b}'.format(self)

    def __iter__(self):
        return (name for name, bit in self._bits.items() if bit & self)

    def __contains__(self, value):
        try:
            return value & self
        except TypeError:
            try:
                return getattr(self, str(value)) & self
            except AttributeError:
                raise ValueError(f'"{value} is not valid bit name of {typename}.')

    def __or__(self, value):
        return self.__class__(int.__or__(self, value))

    def __and__(self, value):
        return self.__class__(int.__and__(self, value))

    def __invert__(self):
        return self.__class__(int.__invert__(self))

    def __format__(self, format_spec):
        return int(self).__format__(format_spec)

    def _set(self, *bits):
        self |= reduce(lambda a, b: a|b, bits, 0)
        return self

    def _unset(self, *bits):
        self &= ~reduce(lambda a, b: a|b, bits, 0)
        return self

    class_namespace = {
        '__doc__': f'{typename}(value)',
        '__slots__': (),
        '_bits': bits,
        '_names': names,
        '__new__': __new__,
        '__repr__': __repr__,
        '__str__': __str__,
        '__iter__': __iter__,
        '__or__': __or__,
        '__and__': __and__,
        '__invert__': __invert__,
        '__format__': __format__,
        '_as_set': _as_set,
        '__contains__': __contains__,
        'set': _set,
        'unset': _unset,
    }

    for index, name in enumerate(value_names):
        class_namespace[name] = 1<<index

    return type(typename, (int,), class_namespace)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
