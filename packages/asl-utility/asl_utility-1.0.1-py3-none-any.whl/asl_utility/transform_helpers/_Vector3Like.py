from abc import ABC, abstractmethod
from typing import TypeVar

import numpy as np

from asl_utility import transform_helpers


class Vector3Like(transform_helpers.ArrayLike, ABC):
    """ Interface class for object that provide Vector3-like functionality.

    This is derived from ``ArrayLike``.
    """
    INDEX_X = 0
    INDEX_Y = 1
    INDEX_Z = 2

    @property
    def x(self) -> float:
        """ Returns the ``INDEX_X`` component of this vector. """
        return float(self.array[Vector3Like.INDEX_X])

    @property
    def y(self) -> float:
        """ Returns the ``INDEX_Y`` component of this vector. """
        return float(self.array[Vector3Like.INDEX_Y])

    @property
    def z(self) -> float:
        """ Returns the ``INDEX_Z`` component of this vector. """
        return float(self.array[Vector3Like.INDEX_Z])


TVector3Like = TypeVar('TVector3Like', bound=Vector3Like)
TVector3LikeOrArray = TypeVar('TVector3LikeOrArray', np.ndarray, Vector3Like)


def default_vector_type_factory(array: np.ndarray) -> np.ndarray:
    return array

