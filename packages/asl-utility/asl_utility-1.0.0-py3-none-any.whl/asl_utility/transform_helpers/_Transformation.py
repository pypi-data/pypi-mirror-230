from __future__ import annotations

import math
from typing import Union, Tuple, List, Callable, overload

import numpy as np
from typing_extensions import Self

from asl_utility import transform_helpers, np_helpers

AcceptedVector3Input = Union[transform_helpers.TVector3LikeOrArray, Tuple[float, float, float], List[float]]
AcceptedComponentVectors = Union[np.ndarray, transform_helpers.ArrayLike, Tuple[float, float, float, float], List[float]]


class Transformation(transform_helpers.ArrayLike):
    """ Immutable datastructure representing a 3d cartesian space spatial transformation. """
    @classmethod
    def identity(cls) -> Self:
        """ Returns an identity transformation, i.e. one that does not apply any change.

        Composing this with other transformations should result in the same as the original.
        Applying this to any rotations/translations does not alter them.

        ``
            v = Vector3([<some values>])

            t = Transformation.identity()

            r = v * t

            assert v == r  # Technically, this should be a proper semantic equality test. Bit it gets the point across...
        ``
        """
        return cls(np.identity(4, dtype=np.float32))

    @classmethod
    def from_row_vectors(cls,
                         r1: AcceptedComponentVectors, r2: AcceptedComponentVectors,
                         r3: AcceptedComponentVectors, r4: AcceptedComponentVectors) -> Self:
        """ Constructs a transformation using the given set of row vectors.

        Note: If you have a list of row vectors (or something similar), you can use Pythons list unpacking semantic:
        ``
            row_vectors = [ ... ]

            t = Transformation.from_row_vectors(*row_vectors)  # Assuming row_vectors has exactly four elements...
        ``
        """
        return cls(np.vstack([r1, r2, r3, r4]))

    @classmethod
    def from_column_vectors(cls,
                            c1: AcceptedComponentVectors, c2: AcceptedComponentVectors,
                            c3: AcceptedComponentVectors, c4: AcceptedComponentVectors) -> Self:
        """ Constructs a transformation using the given set of column vectors.

        Note: If you have a list of column vectors (or something similar), you can use Pythons list unpacking semantic:
        ``
            column_vectors = [ ... ]

            t = Transformation.from_row_vectors(*column_vectors)  # Assuming column_vectors has exactly four elements...
        ``
        """
        return cls(np.transpose(np.vstack([c1, c2, c3, c4])))

    @classmethod
    def from_rotation(cls, q: transform_helpers.Quaternion) -> Self:
        """ Constructs a new transformation with only a rotation part defined by the given quaternion.

        Note: You can compose multiple transformation obtained by this method and its analogues.
        See :func:``~Transformation:from_components``, as it provides exactly that functionality.

        Args:
            q: ``Quaternion`` object representing a rotation.

        Returns:
            ``Transformation`` object representing a rotation transformation.

        """
        m = np.identity(4, dtype=np.float32)
        m[:3, :3] = q.to_matrix()
        return cls(m)

    @classmethod
    def from_translation(cls, v: AcceptedVector3Input) -> Self:
        """ Constructs a new transformation with only a translation part defined by the given vector-like.

        Note: You can compose multiple transformation obtained by this method and its analogues.
        See :func:``~Transformation:from_components``, as it provides exactly that functionality.

        Args:
            v: A 3-element vector-like object representing the translation.

        Returns:
            ``Transformation`` object representing a translation transformation.

        """
        m = np.identity(4, dtype=np.float32)
        m[:3, 3] = np.asarray(v, dtype=np.float32)
        return cls(m)

    @classmethod
    def from_scale(cls, v: AcceptedVector3Input) -> Self:
        """ Constructs a new transformation with only a scaling part defined by the given vector-like.

        Note: You can compose multiple transformation obtained by this method and its analogues.
        See :func:``~Transformation:from_components``, as it provides exactly that functionality.

        Args:
            v: A 3-element vector-like object representing the scaling along the three axes.

        Returns:
            ``Transformation`` object representing a scaling transformation.

        """
        v = np.asarray(v, dtype=np.float32)
        m = np.identity(4, dtype=np.float32)
        m[0, 0] = v[0]
        m[1, 1] = v[1]
        m[2, 2] = v[2]
        return cls(m)

    @classmethod
    def from_translation_and_rotation(cls, v: AcceptedVector3Input, q: transform_helpers.Quaternion) -> Self:
        """ Shortcut method for creating a ``Transformation`` from translation and rotation. """
        m = np.identity(4, dtype=np.float32)
        m[:3, :3] = q.to_matrix()
        m[:3, 3] = np.asarray(v, dtype=np.float32)
        return cls(m)

    @classmethod
    def from_cartesian_pose(cls, p: transform_helpers.CartesianPose):
        """ Shortcut method for creating a ``Transformation`` from a ``CartesianPose`` containing translation and rotation. """
        return cls.from_translation_and_rotation(p.position, p.orientation)

    @classmethod
    def from_components(cls, c: transform_helpers.TransformationComponent) -> Self:
        """ Constructs a new transformation with all the components defined at once.

        This essentially does the following code:
        ``
            t_t = Transformation.from_translation(p)
            t_r = Transformation.from_rotation(q)
            t_s = Transformation.from_scale(s)

            t = t_t * t_r * t_s
        ``


        Args:
            c: ``TransformationComponent`` containing the different components of the resulting transformation.

        Returns:
            ``Transformation`` object composed of the given components.

        """
        T = cls.from_translation(c.translation)
        R = cls.from_rotation(c.rotation)
        S = cls.from_scale(c.scale)

        return T * R * S

    def __init__(self, array: Union[np.ndarray, transform_helpers.ArrayLike]) -> None:
        """ Creates a new ``Transformation`` from the given raw array in row-first order.

        This must be a 4x4 array, or something directly convertible using ``numpy.asarray``.
        The array is then made read-only. If a view is given, a copy will be made first.

        Args:
            array: Numpy ``ndarray`` with shape ``(4, 4)``, or something convertible.
        """
        array = np.asarray(array)

        assert array.shape == (4, 4), "Transformation must be a 4x4 matrix."

        if array.dtype != np.float32:
            array = array.astype(np.float32)

        if array.base is not None:
            array = np.copy(array)

        array.flags.writeable = False
        self._array = array

    def _new_instance(self, array: np.ndarray) -> Self:
        return type(self)(array)

    def get_rotation(self) -> transform_helpers.Quaternion:
        """ Extracts the rotation component of this transformation. """
        cs = self.get_components()
        return cs.rotation

    @overload
    def get_translation(self) -> np.ndarray:
        pass

    @overload
    def get_translation(self, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray]) -> transform_helpers.TVector3LikeOrArray:
        pass

    def get_translation(self, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray] = None) -> transform_helpers.TVector3LikeOrArray:
        """ Extracts the translation component of this transformation.

        Args:
            vector_type_factory (optional): Factory callback for constructing the returned vector.
                Defaults to :func:``~transform_helpers.default_vector_type_factory``.

        Returns:
            vector object (type depending on ``vector_type_factory``) containing the translation component.

        """
        if vector_type_factory is None:
            vector_type_factory = transform_helpers.default_vector_type_factory

        cs = self.get_components()
        return vector_type_factory(cs.translation.array)

    def get_cartesian_pose(self) -> transform_helpers.CartesianPose:
        """ Shortcut for getting a ``CartesianPose`` using the :func:``~Transformation.get_translation`` and :func:``~Transformation.get_rotation`` methods. """
        return transform_helpers.CartesianPose(
            position=self.get_translation(transform_helpers.Vector3),
            orientation=self.get_rotation()
        )

    @overload
    def get_scale(self) -> np.ndarray:
        pass

    @overload
    def get_scale(self, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray]) -> transform_helpers.TVector3LikeOrArray:
        pass

    def get_scale(self, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray] = None) -> transform_helpers.TVector3LikeOrArray:
        """ Extracts the scaling component of this transformation.

        Args:
            vector_type_factory (optional): Factory callback for constructing the returned vector.
                Defaults to :func:``~transform_helpers.default_vector_type_factory``.

        Returns:
            vector object (type depending on ``vector_type_factory``) containing the scaling component.

        """
        if vector_type_factory is None:
            vector_type_factory = transform_helpers.default_vector_type_factory

        # s = np.empty(shape=(3,), dtype=np.float32)
        # s[0] = self._array[0, 0]
        # s[1] = self._array[1, 1]
        # s[2] = self._array[2, 2]

        cs = self.get_components()

        return vector_type_factory(cs.scale.array)

    def get_components(self) -> transform_helpers.TransformationComponent:
        """ Implements a generic component decomposition of the current transformation.

        This decomposes the current transformation into the following parts:
         - translation
         - rotation
         - scale

        Sheer and projection are currently not implemented.

        Returns:
            ``TransformationComponent`` object containing the mentioned components of this transformation.

        """
        t = self._array[:3, 3]

        C = self._array.copy()
        C[:3, 3] = 0
        C_ = np.dot(np.transpose(C), C)
        D = np.identity(4)

        x = 0
        y = 1
        z = 2

        sign = np.sign(np.linalg.det(C))

        D[x, x] = np.sqrt(C_[x, x]) * sign
        D[x, y] = C_[x, y] / D[x, x]
        D[x, z] = C_[x, z] / D[x, x]
        D[y, y] = np.sqrt(C_[y, y] - math.pow(D[x, y], 2)) * sign
        D[y, z] = (C_[y, z] - D[x, y] * D[x, z]) / D[y, y]
        D[z, z] = np.sqrt(C_[z, z] - math.pow(D[x, z], 2) - math.pow(D[y, z], 2)) * sign

        R = np.dot(C, np.linalg.inv(D))

        s = np.empty(3)
        s[x] = D[x, x]
        s[y] = D[y, y]
        s[z] = D[z, z]

        return transform_helpers.TransformationComponent(
            translation=t,
            rotation=transform_helpers.Quaternion.from_matrix(R[:3, :3]),
            scale=s
        )

    @property
    def array(self) -> np.ndarray:
        """ Returns the underlying array for direct numpy access & processing. """
        return self._array

    @property
    def is_identity(self) -> bool:
        """ Returns ``True`` if this transformation is equal to :func:``Transformation.identity``.

        Note: This does an epsilon float check. Is uses ``np_helpers.EPS_THRESHOLD`` as its default absolute tolerance.

        Returns:
            ``True`` if this transformation is equal to identity, otherwise ``False``.

        """
        return np.allclose(self.array, np.identity(4, dtype=np.float32), atol=np_helpers.EPS_THRESHOLD)

    def invert(self) -> Self:
        """ Inverts the current transformation using ``numpy.linalg.inv``.

        That means that the following code should always be true:
        ``
            t = Transformation([<some values>])
            t_inv = t.invert()

            asset (t * t_inv).is_identity
        ``

        If the current transformation is already an identity transformation, it returns the same instance unchanged.


        Returns:
            ``Transformation`` object that represents the inverse transformation of the current one.

        """
        if self.is_identity:
            return self

        return self._new_instance(np.linalg.inv(self.array))

    def __mul__(self, other):
        """ Implements the multiplication (a * b) operator for ``Transformation``.

        This accepts the following arguments:
         - ``Transformation``: Compose this instance with ``other``. See :func:``~Transformation.compose``.

        Args:
            other: ``Transformation`` to compose with.

        Returns:
            ``Transformation`` object representing the composition if ``self`` with ``other``.

        """

        if isinstance(other, Transformation):
            return self.compose(other)

        raise TypeError(f"unsupported operand type(s) for *: 'Transformation' and '{type(other)}'")

    def compose(self, other: Transformation) -> Self:
        """ Composes, i.e. combines this transformation with the given other one,

        If the current instance is an identity transformation, the ``other`` instance is returned (unchanged).
        Similar, if ``other`` is an identity transformation, the current instance is returned.

        Args:
            other: ``Transformation`` object that should the composed with this one.

        Returns:
            ``Transformation`` object that represents the composition of ``self`` and ``other``.

        """
        if self.is_identity:
            return other
        if other.is_identity:
            return self

        result = np.einsum('jk,kl->jl', self.array, other.array)
        return self._new_instance(result)

    @overload
    def apply_vector(self, vector: transform_helpers.TVector3LikeOrArray) -> transform_helpers.TVector3LikeOrArray:
        pass

    @overload
    def apply_vector(self, vector: Union[np.ndarray, Tuple[float, float, float], List[float]],
                     vector_type_factory: Callable[
                         [np.ndarray], transform_helpers.TVector3LikeOrArray]) -> transform_helpers.TVector3LikeOrArray:
        pass

    @overload
    def apply_vector(self, vector: transform_helpers.TVector3LikeOrArray, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray]) -> transform_helpers.TVector3LikeOrArray:
        pass

    def apply_vector(self, vector: AcceptedVector3Input, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray] = None) -> transform_helpers.TVector3LikeOrArray:
        """ Applies this transformation to the given vector.

        Args:
            vector: The vector to transform. Accepts anything that is convertable to a 3-element vector using ``numpy.asarray``.
            vector_type_factory (optional): Factory callback for constructing the resulting vector.
                If ``vector`` is a subclass of ``Vector3Like``, this defaults to that classes constructor.
                Otherwise :func:``~transform_helpers.default_vector_type_factory`` is used.

        Returns:
            vector object (type depending on ``vector_type_factory``) containing ``vector`` transformed by this transformation.

        """
        if vector_type_factory is None:
            if isinstance(vector, transform_helpers.Vector3Like):
                vector_type_factory = type(vector)
            else:
                vector_type_factory = transform_helpers.default_vector_type_factory

        v = np.asarray(vector, dtype=np.float32)

        ev = np_helpers.pad_after_to_length(v, 4, constant_values=1)

        result = np.einsum('jk,k -> j', self.array, ev)
        return vector_type_factory(result[:3])

    def apply_pose(self, pose: transform_helpers.CartesianPose) -> transform_helpers.CartesianPose:
        """ Applies this transformation to a ``CartesianPose``, transforming both ``position`` and ``rotation``. """
        pose_t = self.from_cartesian_pose(pose)
        result_t = self.compose(pose_t)
        return result_t.get_cartesian_pose()
