""" Main transformations package.

This contains classes to represent positions, rotations, full transformations and cartesian poses.

# Basic overview #

``ArrayLike`` and `Vector3Like`` are simple interface classes. They specify the basic abstract interface a class should comply.
``TArrayLike``, ``TArrayLikeOrArray``, ``TVector3Like`` and ``TVector3LikeOrArray`` are ``typing.TypeVar`` definitions matching these interfaces.
They can be used to carry over passed type hints from parameters.

``
def foo(value: TArrayLike) -> TArrayLike:
    # Do something
    return some_new_value_with_same_type(value)


x = MyArrayType()  # Implements ArrayLike

y = foo(x)  # type of y will hint as MyArrayType
``


``Vector3``, ``Quaternion`` and ``Transformation`` are implementations of the respective mathematical concept.
 - ``Vector3``: 3d position/offset in cartesian space
 - ``Quaternion``: Relative rotation or absolute orientation (depending on interpretation)
 - ``Transformation``: Full cartesian spatial transformation, including translation, rotation, scaling (sheering and projection currently not implemented).

The key concept of these is to be expressive in their behavior. In contrast to plain numpy arrays (which they all use under the hood),
these classes tell you exactly what they are, in what state they are and what they can do. Furthermore, they provide simple utility functions
for commonly used operations (like vector normalization, quaternion composition, matrix inversion etc.) directly on the instance.

All of them have a basic constructor taking in a raw numpy array, as well as implement the ``ArrayLike`` interface.
However, for ease of use, they all provide a set of ``from_***()`` class methods and ``to_***()`` instance methods
for converting from and to different representations (e.g Euler angles for a quaternion).

``
rotation = Quaternion.from_axis_and_angle((1, 1, 0), np.pi)  # 180° around the X-Y-diagonal
translation = Vector3([42, 13, 37])

t = Transformation.from_translation_and_rotation(translation, rotation)


transformed = t.apply_vector([10, 20, 30])
``

Please note that these classes are implemented as Immutable. This means that the underlying numpy array is made read-only.
And each operation that would change the instance instead produces a new one.


Finally, ``CartesianPose`` and ``TransformationComponents`` simply server as data holding classes.
As such they are implemented as low-profile ``dataclass`` which only collect multiple related instances
into one expressive structure.

"""

from ._ArrayLike import ArrayLike, TArrayLike, TArrayLikeOrArray
from ._Vector3Like import Vector3Like, TVector3Like, TVector3LikeOrArray, default_vector_type_factory
from ._Vector3 import Vector3
from ._Quaternion import Quaternion
from ._CartesianPosition import CartesianPosition
from ._CartesianPose import CartesianPose
from ._JointPose import JointPose
from ._TransformationComponents import TransformationComponent
from ._Transformation import Transformation

__all__ = [
    ArrayLike, TArrayLike, TArrayLikeOrArray,
    Vector3Like, TVector3Like, TVector3LikeOrArray, default_vector_type_factory,
    Vector3,
    Quaternion,
    CartesianPose,
    JointPose,
    TransformationComponent,
    Transformation
]
