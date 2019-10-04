Documented Universal Errors-and-erasures Reed Solomon Codec written in pure Python
======================================================================

.. image:: https://travis-ci.org/lrq3000/unireedsolomon.svg?branch=master
    :target: https://travis-ci.org/lrq3000/unireedsolomon

Written from scratch by Andrew Brown <brownan@gmail.com> <brownan@cs.duke.edu>
(c) 2010.
Upgraded by Stephen Larroque <LRQ3000@gmail.com> in 2015.

Licensed under the MIT License.

This library implements a pure-Python documented universal Reed-Solomon
error correction codec with a mathematical nomenclatura, compatible with
Python 2.6 up to 3.4 and also with PyPy 2 and PyPy 3.

The project aims to keep a well commented and organized code with
an extensive documentation and mathematical clarity of the various
arithmetic operations.

How does this library differs from other Reed-Solomon libraries?

* **universal**: compatibility with (almost) any other Reed-Solomon codec. This means that you can choose the parameters so that you can either encode data and decode it with another RS codec, or on the opposite encode data with another RS codec and decode this data with this library.
* **errors-and-erasures decoding** allows to decode both erasures (where you know the position of the corrupted characters) and errors (where you don't know where are the corrupted characters) at the same time (because you can decode more erasures than errors, so if you can provide even a few know corrupted characters positions, this can help a lot the decoder to repair the message).
* **documented**: following literate programming guidelines, you should understand everything you need about RS by reading the code and the comments.
* **mathematical nomenclatura**: for example, contrary to most other RS libraries, you will see a clear distinction between the different mathematical constructs, such as the Galois Fields numbers are clearly separated from the generic Polynomial objects, and both are separated from the Reed-Solomon algorithm, which makes use of both of those constructs. For this purpose, object-oriented programming was chosen to design the architecture of the library, although obviously at the expense of a bit of performance. However, this library favors mathematical clarity and documentation over performance (even if performance is optimized whenever possible).
* **pure-Python** means that there are no dependencies whatsoever apart from the Python interpreter. This means that this library should be resilient in the future (since it doesn't depend on external libraries who can become broken with time, see software rot), and you can use it on any system where Python can be installed (including online cloud services).

The authors tried their best to extensively document the algorithms.
However, a lot of the math involved is non-trivial and we can't explain it all
in the comments. To learn more about the algorithms, see these resources:

* `<http://en.wikipedia.org/wiki/Reed–Solomon_error_correction>`_
* `<http://www.cs.duke.edu/courses/spring10/cps296.3/rs_scribe.pdf>`_
* `<http://www.cs.duke.edu/courses/spring10/cps296.3/decoding_rs_scribe.pdf>`_
* `<http://www.cs.cmu.edu/afs/cs.cmu.edu/project/pscico-guyb/realworld/www/reed_solomon.ps>`_
* `<http://www.cs.cmu.edu/afs/cs.cmu.edu/project/pscico-guyb/realworld/www/rs_decode.ps>`_

Also, here's a copy of the presentation one of the authors gave to the class Spring 2010 on his
experience implementing this library. The LaTeX source is in the presentation directory.

`<http://www.cs.duke.edu/courses/spring10/cps296.3/decoding_rs.pdf>`_

The code was lately updated to support errors-and-erasures decoding (both at the same
time), and to be universal (you can supply the parameters to be compatible with almost
any other RS codec).

The codec has decent performances if you use PyPy with the fast methods (~1 MB/s),
but it would be faster if we drop the object-oriented design (implementing everything in
functions), but this would be at the expense of mathematical clarity. If you are interested,
see the reedsolo library by Tomer Filiba, which is exactly the same implementation but
only functional without objects (results in about 5x speedup).

Files
-----
rs.py
    Holds the Reed-Solomon Encoder/Decoder object

polynomial.py
    Contains the Polynomial object (pure-python)

ff.py
    Contains the GF2int object representing an element of the GF(2^p) field, with p being 8 by default (pure-python)

polynomial.pyx
    Cython implementation of polynomial.py with equivalent functions (optional)

ff.pyx
    Cython implementation of ff.py with equivalent functions (optional)

Documentation
-------------
unireedsolomon.rs.RSCoder(n, k, generator=3, prim=0x11b, fcr=1, c_exp=8)
    Creates a new Reed-Solomon Encoder/Decoder object configured with
    the given n and k values.
    n is the length of a codeword, must be less than 256
    k is the length of the message, must be less than n
    generator, prim and fcr parametrize the Galois Field that will be built
    c_exp is the Galois Field range (ie, 8 means GF(2^8) = GF(256)), which is both the limit for one symbol's value, and the maximum length of a message+ecc.

    The code will have error correcting power (ie, maximum number of repairable symbols) of `2*e+v <= (n-k)`, where e is the number of errors and v the number of erasures.

    The typical RSCoder is RSCoder(255, 223)

RSCoder.encode(message, poly=False, k=None)
    Encode a given string with reed-solomon encoding. Returns a byte
    string with the k message bytes and n-k parity bytes at the end.

    If a message is < k bytes long, it is assumed to be padded at the front
    with null bytes (ie, a shortened Reed-Solomon code).

    The sequence returned is always n bytes long.

    If poly is not False, returns the encoded Polynomial object instead of
    the polynomial translated back to a string (useful for debugging)

    You can change the length (number) of parity/ecc bytes at encoding
    by setting k to any value between [1, n-1]. This allows to create only
    one RSCoder and then use it with a variable redundancy rate.

RSCoder.encode_fast(message, poly=False, k=None)
    Same as encode() but using faster algorithms and optimization tricks.

RSCoder.decode(message_ecc, nostrip=False, k=None, erasures_pos=None, only_erasures=False):
    Given a received string or byte array message_ecc (composed of
    a message string + ecc symbols at the end), attempts to decode it.
    If it's a valid codeword, or if there are no more than `2*e+v <= (n-k)` erratas
    (called the Singleton bound), the message is returned.

    You can provide the erasures positions as a list to erasures_pos.
    For example, if you have "hella warld" and you know that `a` is an erasure,
    you can provide the list erasures_pos=[4, 7]. You can correct twice as many
    erasures than errors, and if some provided erasures are wrong (they are correct
    symbols), then there's no problem, they will be repaired just fine (but will count
    towards the Singleton bound). You can also specify that you are sure there are
    only erasures and no errors at all by setting only_erasures=True.

    A message always has k bytes, if a message contained less it is left
    padded with null bytes (punctured RS code). When decoded, these leading
    null bytes are stripped, but that can cause problems if decoding binary data.
    When nostrip is True, messages returned are always k bytes long. This is
    useful to make sure no data is lost when decoding binary data.

    Note that RS can correct errors both in the message and the ecc symbols.

RSCoder.decode_fast(message_ecc, nostrip=False, k=None, erasures_pos=None, only_erasures=False):
    Same as decode() but using faster algorithms and optimization tricks.

RSCoder.check(message_ecc, k=None)
    Verifies the codeword (message + ecc symbols at the end) is valid by testing
    that the code as a polynomial code divides g, or that the syndrome is
    all 0 coefficients. The result is not foolproof: if it's False, you're sure the
    message was corrupted (or that you used the wrong RS parameters),
    but if it's True, it's either that the message is correct, or that there are
    too many errors (ie, more than the Singleton bound) for RS to do anything about it.
    returns True/False

RSCoder.check_fast(message_ecc, k=None)
    Same as check() but using faster algorithms and optimization tricks.

unireedsolomon.ff.find_prime_polynomials(generator=2, c_exp=8, fast_primes=False, single=False)
    Compute the list of prime polynomials for the given generator and
    galois field characteristic exponent. You can then use this prime polynomial
    to specify the mandatory "prim" parameter, particularly if you are using
    a larger Galois Field (eg, 2^16).


Internal API
-------------
Besides the main RSCoder object, two other objects are used in this
implementation: Polynomial and GF2int. Their use is not specifically tied
to the coder or even to the Reed-Solomon algorithm, they are just generic
mathematical constructs respectively representing polynomials and
Galois field's number of base 2.

You do not need to know about the internal API to use the RS codec,
this is just left as a documentation for the reader interested into dwelling
inside the mathematical constructs.

polynomial.Polynomial(coefficients=[], \**sparse)
    There are three ways to initialize a Polynomial object.
    1) With a list, tuple, or other iterable, creates a polynomial using
    the items as coefficients in order of decreasing power

    2) With keyword arguments such as for example x3=5, sets the
    coefficient of x^3 to be 5

    3) With no arguments, creates an empty polynomial, equivalent to
    Polynomial([0])

    >>> print Polynomial([5, 0, 0, 0, 0, 0])
    5x^5

    >>> print Polynomial(x32=5, x64=8)
    8x^64 + 5x^32

    >>> print Polynomial(x5=5, x9=4, x0=2) 
    4x^9 + 5x^5 + 2

Polynomial objects export the following standard functions that perform the
expected operations using polynomial arithmetic. Arithmetic of the coefficients
is determined by the type passed in, so integers or GF2int objects could be
used, the Polynomial class is agnostic to the type of the coefficients.

::

    __add__
    __divmod__
    __eq__
    __floordiv__
    __hash__
    __len__
    __mod__
    __mul__
    __ne__
    __neg__
    __sub__
    evaluate(x)
    degree()
        Returns the degree of the polynomial
    get_coefficient(degree)
        Returns the coefficient of the specified term

ff.GF2int(value)
    Instances of this object are elements of the field GF(2^p) and instances are integers
    in the range 0 to `(2^p)-1`.
    By default, the field is GF(2^8) and instances are integers in the range 0 to 255
    and is defined using the irreducable polynomial 0x11b or in binary form:
    x^8 + x^4 + x^3 + x + 1
    and using 3 as the generator for the exponent table and log table.

    You can however use other parameters for the Galois Field, using the
    init_lut() function.

ff.find_prime_polynomials(generator=2, c_exp=8, fast_primes=False, single=False)
    Find the list of prime polynomials to use to generate the look-up tables
    for your field.

ff.init_lut(generator=3, prim=0x11b, c_exp=8)
    Generate the look-up tables given the parameters. This effectively parametrize
    your Galois Field (ie, generator=2, prim=0x1002d, c_exp=16) will generate
    a GF(2^16) field.

The GF2int class inherits from int and supports all the usual integer
operations. The following methods are overridden for arithmetic in the finite
field GF(2^p)

::

    __add__
    __div__
    __mul__
    __neg__
    __pow__
    __radd__
    __rdiv__
    __rmul__
    __rsub__
    __sub__
    inverse()
        Multiplicative inverse in GF(2^p)


Examples
--------
>>> import rs
>>> coder = rs.RSCoder(20,13)
>>> c = coder.encode("Hello, world!")
>>> print repr(c)
'Hello, world!\x8d\x13\xf4\xf9C\x10\xe5'
>>>
>>> r = "\0"*3 + c[3:]
>>> print repr(r)
'\x00\x00\x00lo, world!\x8d\x13\xf4\xf9C\x10\xe5'
>>>
>>> coder.decode(r)
'Hello, world!'

Image Encoder
~~~~~~~~~~~~~
imageencode.py is an example script that encodes codewords as rows in an image.
It requires PIL to run.

Usage: python imageencode.py [-d] <image file>

Without the -d flag, imageencode.py will encode text from standard in and
output it to the image file. With -d, imageencode.py will read in the data from
the image and output to standard out the decoded text.

An example is included: ``exampleimage.png``. Try decoding it as-is, then open
it up in an image editor and paint some vertical stripes on it. As long as no
more than 16 pixels per row are disturbed, the text will be decoded correctly.
Then draw more stripes such that more than 16 pixels per row are disturbed and
verify that the message is decoded improperly.

Notice how the parity data looks different--the last 32 pixels of each row are
colored differently. That's because this particular image contains encoded
ASCII text, which generally only has bytes from a small range (the alphabet and
printable punctuation). The parity data, however, is binary and contains bytes
from the full range 0-255. Also note that either the data area or the parity
area (or both!) can be disturbed as long as no more than 16 bytes per row are
disturbed.

Cython implementation
~~~~~~~~~~~~~~~~~~

If either a C compiler or Cython is found, rs.py will automatically load the Cython implementations
(the *.pyx files).
These are provided as optimized versions of the pure-python implementations, with equivalent
functionalities. The goal was to get a speedup, which is the case, but using PyPy on the pure-python
implementation provides a significantly higher speedup than the Cython implementation.
The Cython implementations are still provided for the interested reader, but the casual user is
not advised to use them. If you want to encode and decode fast, use PyPy.


