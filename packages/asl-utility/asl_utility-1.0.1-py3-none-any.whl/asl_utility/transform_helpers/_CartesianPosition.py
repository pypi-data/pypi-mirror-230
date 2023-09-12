from typing import Union, Tuple, List
from deprecated import deprecated


import numpy as np
from typing_extensions import Self

from asl_utility import transform_helpers, np_helpers


@deprecated(version="0.1.0rc0", reason="Fully replaced by Vector3 class")
class CartesianPosition(transform_helpers.Vector3Like):

    @classmethod
    def zero(cls) -> Self:
        return cls(np.asarray([0, 0, 0], dtype=np.float32))

    @classmethod
    def from_values(cls, x: float, y: float, z: float) -> Self:
        return cls(np.asarray([x, y, z]))

    def __init__(self, array: Union[np.ndarray, transform_helpers.Vector3Like, Tuple[float, float, float], List[float]]):
        array = np.asarray(array)

        assert array.shape == (3,), "CartesianPosition must be a three element vector."

        if array.dtype != np.float32:
            array = array.astype(np.float32)

        if array.base is not None:
            array = np.copy(array)

        array.flags.writeable = False
        self._array = array

    @property
    def array(self) -> np.ndarray:
        return self._array

    @property
    def is_zero(self) -> bool:
        return np.allclose(self.array, np.asarray([0, 0, 0], dtype=np.float32), atol=np_helpers.EPS_THRESHOLD)

