"""
This module contains functions to generate CUDA snippers for datatypes and
defining variables from numpy.
"""

import numpy as np


# Map to convert simple numpy data types to CUDA data types
TYPE_MAP = {
    np.int8: 'signed char',
    np.uint8: 'char',
    np.int16: 'short',
    np.uint16: 'ushort',
    np.int32: 'int',
    np.uint32: 'uint',
    np.int64: 'long',
    np.uint64: 'ulong',
    np.float32: 'float',
    np.float64: 'double',
}


def get_cuda_struct(dtype):
    """
    Generates a snippet for a structure data type from a tuple numpy `dtype`.
    """
    if dtype.type is np.void or dtype.type is np.record:
        fields_lines = []
        for key, tpl in dtype.fields.items():
            ts = get_cuda_type(tpl[0], key)
            fields_lines.append(f"{ts};\n")
        return "struct {\n%s}" % ''.join(fields_lines)
    else:
        raise TypeError(f"{dtype} is not a struct")


def get_cuda_type(dtype, name=None):
    """
    Generates a snippet for a variable defining with the name `name` and
    the type corresponding to numpy `dtype`. If `name` is `None`, just the type
    name will be returned.
    """
    if dtype.type in TYPE_MAP:
        return _gen_simple_type(TYPE_MAP[dtype.type], name)

    elif dtype.type is np.bytes_:
        return _gen_array_type("char", dtype.itemsize, name)

    else:
        raise TypeError(f"Unknown numpy type: {dtype}")


def dataframe_to_records(df, column_dtypes, align=False):
    """
    Converts a pandas DataFrame to numpy records.
    It works similar to DataFrame.to_records()
    but it has 'align' flag such that if 'align=True' the function prepares
    correct alignment of the bytes as in C structs.
    Only the columns listed in column_dtypes will be represented
    in the final records.

    Example:

        records = dataframe_to_records(
            df,
            column_dtypes=[
                ('key', 'S4'),
                ('x', np.uint8),
                ('y', np.uint16),
            ]
        )
    """
    columns = [col[0] for col in column_dtypes]
    records = df[columns].to_records(index=False)
    return np.array(records, dtype=np.dtype(column_dtypes, align=align))


def _gen_simple_type(type_, name):
    return type_ if name is None else f"{type_} {name}"


def _gen_array_type(type_, size, name):
    return f"{type_}[{size}]" if name is None else f"{type_} {name}[{size}]"
