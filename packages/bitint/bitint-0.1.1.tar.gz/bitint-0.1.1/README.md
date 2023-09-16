# bit-int

Pure Python implementation of extended integer with named bits.

I found that some Python engineers find working with bit math as sets
unnatural. So I created this simple `int` extension to make bit manipulation
more Pythonic and to demonstrate the beauty of Python magic.

What is BitInt good for in real life? It's as efficient as Python's own `set`
type but it can be easily stored in databases, JSON or shared with other
languages without any modification (C, Go, Java, JavaScript).

BitInt is highly inspired by great
[namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple)
from python standard library.

## Installation

    pip install 'git+https://github.com/czervenka/bit-set.git'

or pipenv

    pipenv install -e 'git+https://github.com/czervenka/bit-set.git#egg=bitint'

## Usage

    >>> from bitint import bitint

BitInt is an integer type where bits can be named and manipulated as a set.
Let's create a class Animals with first 8 bits named after animals kinds:

    >>> Animals = bitint('Animals', 'cat, dog, mouse, bee, turtle, snake, frog, axolotl')

In this case, animals are represented by bits where cat is the first bit
(2^0=1), dog is the second (2^1=2), mouse the third (2^2=4). You don't need to
remember which animal is represented by which bit, because each species bit value
is stored in property named after the species label:

    >>> Animals.cat
    1

Similarly `dog` label represents the second bit, which has value `2**1 = 2`

    >>> Animals.dog
    2

We can now instantiate a subset of animals with set bits which corresponds to amphibians...

    >>> amphibians = Animals('frog', 'axolotl')

... or animals which are commonly pets...

    >>> pets = Animals('cat', 'dog')

Bit representation of `pets` is

    0 0 0 0 0 0 1 1
                ^ ^
                | L cat (2^0 == 1 == Animals.cat)
                L dog (2^1 == 2 == Animals.dog)

Having this two sets of animals, we can use bit magic to test whether an animal
bit is set to 1 or 0:

    >>> "Dog is a pet" if Animals.dog & pets else "Dog is not a pet"
    'Dog is a pet'

... or use `in` operator:

    >>> Animals.dog in pets
    True

What about if we try to check existence of an animal which has not been defined
yet?

    >>> Animals.elefant in pets
    Traceback (most recent call last):
      ...
    AttributeError: type object 'Animals' has no attribute 'elefant'

Beside checking for existense, it's possible to make basic set operations.  For
example, we can create a new Animals bitint which includes all pets and
amphibians:

    >>> pets | amphibians
    Animals('cat', 'dog', 'frog', 'axolotl')

We can also find an intersection:

    >>> hairy_animals = Animals('cat', 'dog', 'mouse')
    >>> hairy_animals & pets
    Animals('cat', 'dog')

... and even complement

    >>> ~pets
    Animals('mouse', 'bee', 'turtle', 'snake', 'frog', 'axolotl')

A set of all animals can be created using bit inversion of no animal

    >>> all_animals = ~Animals()
    >>> all_animals
    Animals('cat', 'dog', 'mouse', 'bee', 'turtle', 'snake', 'frog', 'axolotl')

Animals can be added or removed from all animals by `set` and `unset`

    >>> all_animals.unset(Animals.dog, Animals.bee, Animals.snake)
    Animals('cat', 'mouse', 'turtle', 'frog', 'axolotl')


If you are curious which bits are set for named flags, print a bitint value.

    >>> print(amphibians)
    11000000
    >>> print(pets | amphibians)
    11000011

Furthermore you can also create list of or iterate over names of set bits

    >>> list(pets)
    ['cat', 'dog']
    >>> for pet in pets:
    ...     print(pet)
    cat
    dog

or for instance create regular Python set

    >>> set(pets) == {'cat', 'dog'}
    True

Beside everything else BitInt is just an enhanced integer :)

    >>> pets + 1
    4
    >>> import json
    >>> json.dumps({"pets_bitint": pets})
    '{"pets_bitint": 3}'


**Tip:** If you change the named bits of a BitInt class (e.g. replace 'dog'
with 'elephant') and you have stored bitints you need to make a migration
otherwise all dogs become elephants. If you want to avoid migrations, never
change existing named bit and only add new at the end of definition to utilize
unused bits.



**Update:** My daughter found a bug in this readme:

    >>> pets |= Animals.axolotl
    >>> list(pets)
    ['cat', 'dog', 'axolotl']

## Testing

Tests are documentation and vice-versa:

    python -m doctest bitint.py README.md

