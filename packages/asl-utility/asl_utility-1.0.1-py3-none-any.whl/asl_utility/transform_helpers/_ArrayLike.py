from abc import ABC, abstractmethod
from typing import TypeVar, cast

import numpy as np


class ArrayLike(ABC):
    """ Interface class for object that provide array-like functionality. """
    @property
    @abstractmethod
    def array(self) -> np.ndarray:
        """ Provides access to a numpy array representation.

        Usually, this simply returns the underlying array. However, if an implementation does not use Numpy as a data backend,
        this must return a suitable interface or conversion.

        Note: The returned array might (and quite often is) read-only. So for any modifications to the result,
        a copy must be made.
        """
        raise NotImplementedError()

    def __array__(self, dtype: np.dtype = None):
        a = self.array
        if dtype is None or dtype == a.dtype:
            return a
        return a.astype(dtype)


TArrayLike = TypeVar('TArrayLike', bound=ArrayLike)
TArrayLikeOrArray = TypeVar('TArrayLikeOrArray', np.ndarray, ArrayLike)
