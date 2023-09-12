import dataclasses
from typing import Union, Tuple, List

import numpy as np
from typing_extensions import Self

from asl_utility import transform_helpers


@dataclasses.dataclass(frozen=True)
class TransformationComponent:
    """ Data holding class for the different components of a ``Transformation``. """
    translation: transform_helpers.Vector3
    rotation: transform_helpers.Quaternion
    scale: transform_helpers.Vector3

    @classmethod
    def identity(cls) -> Self:
        """ Returns a ``TransformationComponent`` that only contains ``identity`` values. """
        return TransformationComponent(
            translation=transform_helpers.Vector3.identity(),
            rotation=transform_helpers.Quaternion.identity(),
            scale=transform_helpers.Vector3.one()
        )

    def __init__(self,
                 translation: Union[np.ndarray, transform_helpers.Vector3Like, Tuple[float, float, float], List[float]] = None,
                 rotation: Union[np.ndarray, transform_helpers.ArrayLike, Tuple[float, float, float, float], List[float]] = None,
                 scale: Union[np.ndarray, transform_helpers.Vector3Like, Tuple[float, float, float], List[float]] = None):
        """ Constructs a new instance of ``TransformationComponent`` using (optional) components.

        All components are optional. If not given, they default to a no-op (identity) value.

        Args:
            translation (optional): Either a ``Vector3`` instance, or anything that is accepted by its constructor.
                Defaults to :func:``~Vector3.identity``.
            rotation (optional): Either a ``Quaternion`` instance, or anything that is accepted by its constructor.
                Defaults to :func:``~Quaternion.identity``.
            scale (optional): Either a ``Vector3`` instance, or anything that is accepted by its constructor.
                Defaults to :func:``~Vector3.identity``.
        """

        if translation is not None:
            translation = transform_helpers.Vector3(translation)
        else:
            translation = transform_helpers.Vector3.identity()

        if rotation is not None:
            rotation = transform_helpers.Quaternion(rotation)
        else:
            rotation = transform_helpers.Quaternion.identity()

        if scale is not None:
            scale = transform_helpers.Vector3(scale)
        else:
            scale = transform_helpers.Vector3.one()

        object.__setattr__(self, 'translation', translation)
        object.__setattr__(self, 'rotation', rotation)
        object.__setattr__(self, 'scale', scale)

