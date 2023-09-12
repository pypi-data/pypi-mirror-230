import dataclasses
from typing import Union, Tuple, List

import numpy as np
from typing_extensions import Self

from asl_utility import transform_helpers


@dataclasses.dataclass(frozen=True)
class CartesianPose:
    """ Data holding class for 3d poses in cartesian space.

    This is simply a ``Vector3`` for ``position`` and ``Quaternion`` for ``orientation``.

    """
    position: transform_helpers.Vector3
    orientation: transform_helpers.Quaternion

    @classmethod
    def identity(cls) -> Self:
        """ Returns a ``CartesianPose`` that only contains ``identity`` values. """
        return CartesianPose(
            position=transform_helpers.Vector3.identity(),
            orientation=transform_helpers.Quaternion.identity()
        )

    def __init__(self, position: Union[np.ndarray, transform_helpers.Vector3Like, Tuple[float, float, float], List[float]],
                 orientation: Union[np.ndarray, transform_helpers.ArrayLike, Tuple[float, float, float, float], List[float]]):
        """ Creates a new instance of a ``CartesianPose`` from a position and orientation.

        Note that this accepts any representation that ``Vector3`` and ``Quaternion`` accept for their respective constructor, too.

        Args:
            position: Either a ``Vector3`` instance, or anything that is accepted by its constructor.
            orientation: Either a ``Quaternion`` instance, or anything that is accepted by its constructor.
        """
        object.__setattr__(self, 'position', transform_helpers.Vector3(position))
        object.__setattr__(self, 'orientation', transform_helpers.Quaternion(orientation))

