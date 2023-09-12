# Imports
from typing import Union, TypeVar, Any, Tuple, List, Iterable, T

import numpy as np
import numpy.typing as npt


ArrayLike = Union[int, float, np.ndarray]


EPS_THRESHOLD: float = np.finfo(np.float32).eps * 4.0
PRECISION: int = np.finfo(np.float32).precision


def allclose(a, b) -> bool:
    """ Wrapper for numpy.allclose() that uses float32 EPS as tolerance.

    This effectively checks if two floats are the same except for what rounding errors can occur on lower digits.

    Args:
        a: array_like
            Input array to compare.
        b: array_like
            Input array to compare.
        a, b :

    Returns: bool
        Returns True if the two arrays are equal within the given
        tolerance; False otherwise.
    """
    return np.allclose(a, b, atol=EPS_THRESHOLD, rtol=0)


def round_to_precision(a: T) -> T:
    """ Wrapper function for numpy.around() that rounds the given value or array to the maximum float32 precision.

    Args:
        a : array_like
            Input data.

    Returns:
        rounded_array : ndarray
            An array of the same type as `a`, containing the rounded values.

            The real and imaginary parts of complex numbers are rounded
            separately.  The result of rounding a float is a float.

    """
    return np.around(a, decimals=PRECISION)


def normalize(array: np.ndarray) -> np.ndarray:
    """ Normalizes the given array, if it not allreay is.

    Args:
        array: And arbitrary numpy array.

    Returns: An array that is normalized. If the input was already, the same array is returned.

    """

    norm = np.linalg.norm(array)
    if norm < EPS_THRESHOLD:
        return array
    return array / norm


def clip_circular(value: ArrayLike, minimum: ArrayLike, maximum: ArrayLike) -> ArrayLike:
    """ Clips values to an interval, but shifts out-of-bounds values to their relative position inside the interval.

    Args:
        value: Array-like value, that should be clipped.
        minimum: Array-like inclusive minimum bound of the interval.
        maximum: Array-like exclusive maximum  bound of the interval.

    Returns:
        Value clipped to the given interval, remapping in a circular manner.
    """
    return np.mod(value - minimum, (maximum - minimum)) + minimum


def pad_before_to_length(array: npt.ArrayLike, length: Union[int, Tuple, List[int]], *, dtype: np.dtype = None,
                         constant_values: Union[Any, Tuple[Any, Any], List[Tuple[Any, Any]]] = 0.0):
    """ Pads the given array at the start of each axis to a specified length.

    Args:
        array: The array to pad.
        length: Length to pad to.
        dtype: Datatype of returned array.
        constant_values: Values to pad to. Defaults to 0.0

    Returns:
        A new padded array

    """
    return _pad(array, length, 0, dtype=dtype, constant_values=constant_values)


def pad_after_to_length(array: npt.ArrayLike, length: Union[int, Tuple, List[int]], *, dtype: np.dtype = None,
                        constant_values: Union[Any, Tuple[Any, Any], List[Tuple[Any, Any]]] = 0.0):
    """ Pads the given array at the end of each axis to a specified length.

    Args:
        array: The array to pad.
        length: Length to pad to.
        dtype: Datatype of returned array.
        constant_values: Values to pad to. Defaults to 0.0

    Returns:
        A new padded array

    """
    return _pad(array, length, 1, dtype=dtype, constant_values=constant_values)


def _pad(array: npt.ArrayLike, length: Union[int, Tuple, List[int]], index, *, dtype: np.dtype = None,
         constant_values: Union[Any, Tuple[Any, Any], List[Tuple[Any, Any]]] = 0.0):
    array = np.asarray(array)

    if dtype is None:
        dtype = array.dtype

    if not isinstance(length, Iterable):
        length = (length,)
    length = np.asarray(length)
    if len(length.shape) < len(array.shape):
        length = np.repeat(length, len(array.shape) - len(length.shape))

    s_t = np.zeros(shape=(len(array.shape), 2), dtype=int)
    s_t[:, index] = np.maximum(length - np.asarray(array.shape), 0)

    res = np.pad(array, s_t, constant_values=constant_values).astype(dtype)
    return res

