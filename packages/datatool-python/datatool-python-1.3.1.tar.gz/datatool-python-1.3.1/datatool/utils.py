"""
This moduls contains separate helpful functions that have not been places
to other modules on the library by sense.
"""

from itertools import islice


def as_chunks(it, chunk_size):
    """
    A generator that prepares chunk with fixed size (equals to 'chunk_size')
    from given iterable object 'it'. Each chunk is a list.

    Example:

        it = iter(range(12))

        for chunk in as_chunks(it, 5):
            print(chunk)
    """
    it = iter(it)
    while True:
        chunk = list(islice(it, chunk_size))
        if not chunk:
            break
        yield chunk


def as_iter_chunks(it, chunk_size):
    """
    A generator that prepares chunk with fixed size (equals to 'chunk_size')
    from given iterable object 'it'. Each chunk is a generator also.

    Example:

        it = iter(range(12))

        for chunk in as_iter_chunks(it, 5):
            for elem in chunk:
                print(elem, end=" ")
            print()
    """
    while True:
        try:
            first = next(it)
        except StopIteration:
            break
        else:
            yield _chunk_iter(it, chunk_size, first)


def as_grid(lst1, lst2):
    """
    A generator that yields all the pairs of the elements in two given lists.
    """
    yield from (
        (e1, e2) for e1 in lst1 for e2 in lst2
    )


def _chunk_iter(it, chunk_size, first):
    """
    A generator that represents a separate chunk. It yields first chunk_size
    elements from given 'it' supposing that first element has already taken
    from 'it' before and passed as an argument. This generator is used in
    the function 'as_chunks'.
    """
    yield first
    for _ in range(1, chunk_size):
        try:
            yield next(it)
        except StopIteration:
            break
