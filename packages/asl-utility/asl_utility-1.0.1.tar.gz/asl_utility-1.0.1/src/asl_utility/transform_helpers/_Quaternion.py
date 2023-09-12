from __future__ import annotations

import math
import warnings
from typing import Tuple, Union, Optional, List, TypeVar, Type, Callable, cast, overload, Sequence, Iterable
from typing_extensions import Self

import numpy as np

from asl_utility import np_helpers, transform_helpers

AcceptedVector3Input = Union[transform_helpers.TVector3LikeOrArray, Tuple[float, float, float], List[float]]
AcceptedVector4Input = Union[transform_helpers.TArrayLikeOrArray, Tuple[float, float, float, float], List[float]]


def _sequence_to_axis_list(sequence: str) -> Tuple[List[Tuple[int, int, int]], bool]:
    axis_map = {
        "x": (1, 0, 0),
        "y": (0, 1, 0),
        "z": (0, 0, 1)
    }
    seq_set = set(sequence)

    intrinsic = False
    if seq_set.issubset({"X", "Y", "Z"}):
        intrinsic = True
        sequence = sequence.lower()
    elif not seq_set.issubset({"x", "y", "z"}):
        raise ValueError("Expected axes from `sequence` to be from "
                         "['x', 'y', 'z'] or ['X', 'Y', 'Z'], "
                         "got {}".format(sequence))

    if any(sequence[i] == sequence[i+1] for i in range(2)):
        raise ValueError("Expected consecutive axes to be different, "
                         "got {}".format(sequence))

    del seq_set

    return [axis_map[axis] for axis in sequence], intrinsic


class Quaternion (transform_helpers.ArrayLike):
    """ Quaterion class representing (and implementing) spatial rotations in 3d cartesian space in JPL notation (x, y, z, w).

    Note: This class is immutable. This means the underlying numpy array is made read-only.
    And each operation that would manipulate its content instead returns a new instance.

    Libraries might derive from this class to add special behavior or extra/additional information.
    To do this, one must override the constructor as well as ``_new_instance()`` method.
    """
    INDEX_X = 0
    INDEX_Y = 1
    INDEX_Z = 2
    INDEX_W = 3
    INDEX_IMAGINARY = slice(None, 3)

    @classmethod
    def identity(cls) -> Self:
        """ Returns an identity quaternion, i.e. one that does not apply any rotation.

        Composing other quaternions with this should result in the same original. And applying this to a vector should not change it.
        ``
            q = Quaternion([<some values>])

            i = Quaternion.identity()

            r = q * i

            assert q == r  # Technically, this should be a proper semantic equality test. Bit it gets the point across...
        ``
        """
        return cls(np.asarray([0, 0, 0, 1], dtype=np.float32))

    @classmethod
    def from_axis_and_angle(cls, axis: AcceptedVector3Input, angle: Union[float, int, np.ndarray], *, degrees: bool = False) -> Self:
        """ Create a new quaterion that represents a rotation around the given axis by the given angle.

        Args:
            axis: The 3d axis around the rotation should be. This can be any 3d vector.
            angle: The angle of rotation. If a numpy array is given, it must be of 1-element length.
            degrees: If ``True``, given angles are in degrees. Otherwise, radians are used. Optional, default to False.

        Returns:
            ``Quaternion`` object representing the specified rotation.

        """
        quaternion = np.zeros((4,), dtype=np.float32)

        if degrees:
            angle = np.deg2rad(angle)

        quaternion[:3] = np.asarray(axis, dtype=np.float32)

        qlen = np.linalg.norm(quaternion)
        if qlen > np_helpers.EPS_THRESHOLD:
            quaternion *= math.sin(angle / 2.0) / qlen

        quaternion[3] = math.cos(angle / 2.0)

        return cls(quaternion)

    about_axis = from_axis_and_angle

    @classmethod
    def from_values(cls, x: float, y: float, z: float, w: float) -> Self:
        """ Creates a new quaterion from the given four component values.

        Args:
            x: The first imaginary component.
            y: The second imaginary component.
            z: The third imaginary component.
            w: The real component.

        Returns:
            ``Quaternion`` object with the given component values.
        """
        return cls(np.asarray([x, y, z, w]))

    @classmethod
    def from_vector_and_scalar(cls, v: np.ndarray, w: float) -> Self:
        """ Similar to ``from_values()``, creates a new quaternion from the given imaginary and read part.

        Args:
            v: The three imaginary components in one array.
            w: The real component.

        Returns:
            ``Quaternion`` object with the given component values.
        """
        return cls(np.hstack([v, np.asarray([w])]))

    @classmethod
    def from_matrix(cls, matrix: Union[np.ndarray, transform_helpers.ArrayLike]) -> Self:
        """ Creates a new quaternion from a 3x3 rotation matrix.

        See `<https://en.wikipedia.org/wiki/Rotation_matrix#In_three_dimensions>_.

        Note: The matrix must be in row-first order.

        Args:
            matrix: A 3x3 matrix representing a 3d rotation.

        Returns:
            ``Quaternion`` object representing the same rotation as the given matrix.
        """
        matrix = np.asarray(matrix, dtype=np.float32)

        if matrix.shape != (3, 3):
            raise ValueError(f'Expected a 3x3 rotation matrix, got array with shape {matrix.shape}.')

        diag_and_trace = np.empty((4, ))
        diag_and_trace[:3] = matrix.diagonal()  # Get diagonal...
        diag_and_trace[-1] = trace = diag_and_trace[:3].sum()  # ...and create a trace from it

        largest_component_index = diag_and_trace.argmax()

        quat = np.empty((4,), dtype=np.float32)

        if largest_component_index != 3:  # It's not the trace, so one (qx, qy, or qz) is >0.5
            i = largest_component_index
            j = (i + 1) % 3
            k = (j + 1) % 3

            quat[i] = 1 - trace + 2 * matrix[i, i]
            quat[j] = matrix[j, i] + matrix[i, j]
            quat[k] = matrix[k, i] + matrix[i, k]
            quat[3] = matrix[k, j] - matrix[j, k]
        else:

            quat[0] = matrix[2, 1] - matrix[1, 2]
            quat[1] = matrix[0, 2] - matrix[2, 0]
            quat[2] = matrix[1, 0] - matrix[0, 1]
            quat[3] = 1 + trace

        quat = np_helpers.normalize(quat)

        return cls(quat)

    @classmethod
    def from_euler(cls, sequence: str, angles: Union[np.ndarray, transform_helpers.ArrayLike, Sequence[Union[float, int]]], *, degrees: bool = False) -> Self:
        """ Create a rotation quaternion form euler angles in the given axis order.


        Args:
            sequence:
                Specifies sequence of axes for rotations. Up to 3 characters belonging to the set {‘X’, ‘Y’, ‘Z’} for intrinsic
                rotations, or {‘x’, ‘y’, ‘z’} for extrinsic rotations. Extrinsic and intrinsic rotations cannot be mixed in one function call.
            angles:
                Euler angles for the given axes.
            degrees:
                If True, then the given angles are assumed to be in degrees. Default is False.

        Returns:
            ``Quaternion`` object representing the rotation defined by the given angles around the given axes.

        """
        axis_sequence, intrinsic = _sequence_to_axis_list(sequence)

        res = cls.identity()
        
        for axis, angle in zip(axis_sequence, angles):
            if intrinsic:
                res = res * cls.about_axis(axis, angle, degrees=degrees)
            else:
                res = cls.about_axis(axis, angle, degrees=degrees) * res

        return res

    def __init__(self, array: Union[np.ndarray, transform_helpers.ArrayLike, Tuple[float, float, float, float], List[float]]) -> None:
        """ Creates a quaterion from the given raw array.

        This must be a 4-element array, or something directly convertible using ``numpy.asarray``.
        The array is then made read-only. If a view is given, a copy will be made first.

        Args:
            array: A 4-element numpy array or somthing convertible.
        """
        array = np.asarray(array)

        assert array.shape == (4,), "Quaternions must be a four element vector."

        if array.dtype != np.float32:
            array = array.astype(np.float32)

        if array.base is not None:
            array = np.copy(array)

        array.flags.writeable = False
        self._array = array

    def _new_instance(self, array: np.ndarray):
        return type(self)(array)

    def __str__(self):
        """ Converts the quaternion to a readable string representation. """
        return f'Q{("(I)" if self.is_identity else "")}{str(self.array)}'

    def __repr__(self):
        """ Converts the quaternion to a readable string representation. Same as :func:``~Quaternion.__str__``. """
        return str(self)

    def to_matrix(self) -> np.ndarray:
        """ Converts the quaternion to a 3d rotation matrix.

        This is the analogue method to :func:`~Quaterion.from_matrix`.

        Returns:
            A numpy ``ndarray`` with shape ``(3, 3)`` that is a row-first matrix representing a 3d rotation.
        """

        x = self.x
        y = self.y
        z = self.z
        w = self.w

        x2 = x * x
        y2 = y * y
        z2 = z * z
        w2 = w * w

        xy = x * y
        zw = z * w
        xz = x * z
        yw = y * w
        yz = y * z
        xw = x * w

        matrix = np.empty((3, 3), dtype=np.float32)

        matrix[0, 0] = x2 - y2 - z2 + w2
        matrix[1, 0] = 2 * (xy + zw)
        matrix[2, 0] = 2 * (xz - yw)

        matrix[0, 1] = 2 * (xy - zw)
        matrix[1, 1] = - x2 + y2 - z2 + w2
        matrix[2, 1] = 2 * (yz + xw)

        matrix[0, 2] = 2 * (xz + yw)
        matrix[1, 2] = 2 * (yz - xw)
        matrix[2, 2] = - x2 - y2 + z2 + w2

        return matrix

    # noinspection PyPep8Naming
    def to_euler(self, sequence: str, *, degrees: bool = False) -> np.ndarray:
        """ Generates generic Euler or Tait-Bryan angles in the given sequence from this Quaternion. The implementation
        is inspired by and designed to be compatible with `scipy.spatial.transform.Rotation.as_euler()`.

        Similar to scipy, this uses the algorithm described in Malcolm D. Shuster, F. Landis Markley, “General formula for extraction the Euler angles”,
        Journal of guidance, control, and dynamics, vol. 29.1, pp. 215-221. 2006 for computation.

        Euler angles suffer from the problem of gimbal lock, where the representation loses a degree of freedom and it
        is not possible to determine the first and third angles uniquely. In this case, a warning is raised, and the
        third angle is set to zero. Note however that the returned angles still represent the correct rotation.

        Args:
            sequence:
                3 characters belonging to the set {‘X’, ‘Y’, ‘Z’} for intrinsic rotations, or {‘x’, ‘y’, ‘z’} for extrinsic rotations.
                Adjacent axes cannot be the same. Extrinsic and intrinsic rotations cannot be mixed in one function call.
            degrees:
                Returned angles are in degrees if this flag is True, else they are in radians. Default is False.
        Returns:
            Numpy ``ndarray`` with shape ``(3, )``, each element representing one respective angle of the given sequence.
        """
        axis_sequence, intrinsic = _sequence_to_axis_list(sequence)

        if self.is_identity:
            return np.zeros(3, dtype=np.float32)

        if not intrinsic:
            axis_sequence = axis_sequence[::-1]

        n1 = axis_sequence[0]
        n2 = axis_sequence[1]
        n3 = axis_sequence[2]

        sin_lambda = np.dot(np.cross(n1, n2), n3)
        cos_lambda = np.dot(n1, n3)
        lambda_ = math.atan2(sin_lambda, cos_lambda)

        R_trans = np.asarray([
            [1, 0, 0],
            [0, cos_lambda, sin_lambda],
            [0, -sin_lambda, cos_lambda]
        ], dtype=np.float32)

        C_trans = np.empty((3, 3), dtype=np.float32)
        C_trans[0, :] = n2
        C_trans[1, :] = np.cross(n1, n2)
        C_trans[2, :] = n1

        matrix = self.to_matrix()

        O_trans = C_trans.dot(matrix).dot(C_trans.transpose()).dot(R_trans)

        upsilon_ = math.acos(np.clip(O_trans[2, 2], -1, 1))

        close_to_lambda = np_helpers.allclose(abs(upsilon_), 0)
        close_to_lambda_pi = np_helpers.allclose(abs(upsilon_), np.pi)
        degenerate = close_to_lambda or close_to_lambda_pi

        upsilon = upsilon_ + lambda_

        if not degenerate:
            phi = math.atan2(O_trans[0, 2], -O_trans[1, 2])
            psi = math.atan2(O_trans[2, 0], O_trans[2, 1])
        else:
            if intrinsic:
                # Order is phi upsilon psi -> psi = 0
                psi = 0
                if close_to_lambda:
                    phi = math.atan2(O_trans[1, 0] - O_trans[0, 1], O_trans[0, 0] + O_trans[1, 1])
                else:
                    assert close_to_lambda_pi
                    phi = -math.atan2(O_trans[1, 0] + O_trans[0, 1], O_trans[0, 0] - O_trans[1, 1])
            else:
                # Application order is psi upsilon phi -> phi = 0
                phi = 0
                if close_to_lambda:
                    psi = math.atan2(O_trans[1, 0] - O_trans[0, 1], O_trans[0, 0] + O_trans[1, 1])
                else:
                    assert close_to_lambda_pi
                    psi = math.atan2(O_trans[1, 0] + O_trans[0, 1], O_trans[0, 0] - O_trans[1, 1])

        # Adjust angles
        if sequence[0] == sequence[2]:
            adjust = upsilon < 0 or upsilon > np.pi
        else:
            adjust = upsilon < -np.pi/2 or upsilon > np.pi/2

        if adjust and not degenerate:
            phi += np.pi
            upsilon = 2 * lambda_ - upsilon
            psi -= np.pi

        phi = np_helpers.clip_circular(phi, -np.pi, np.pi)
        upsilon = np_helpers.clip_circular(upsilon, -np.pi, np.pi)
        psi = np_helpers.clip_circular(psi, -np.pi, np.pi)

        if degenerate:
            warnings.warn("Gimbal lock detected. Setting third angle to zero since it is not possible to uniquely determine all angles.")

        if intrinsic:
            res = np.asarray([phi, upsilon, psi], dtype=np.float32)
        else:
            res = np.asarray([psi, upsilon, phi], dtype=np.float32)

        if degrees:
            res = np.rad2deg(res)
        return res

    @property
    def array(self) -> np.ndarray:
        """ Returns the underlying array for direct numpy access & processing. """
        return self._array

    @property
    def x(self) -> float:
        """ Returns the first imaginary component. """
        return float(self._array[Quaternion.INDEX_X])

    @property
    def y(self) -> float:
        """ Returns the second imaginary component. """
        return float(self._array[Quaternion.INDEX_Y])

    @property
    def z(self) -> float:
        """ Returns the third imaginary component. """
        return float(self._array[Quaternion.INDEX_Z])

    @property
    def w(self) -> float:
        """ Returns the real component. """
        return float(self._array[Quaternion.INDEX_W])

    @property
    def imaginary(self) -> np.ndarray:
        """ Returns the imaginary components. """
        return self._array[Quaternion.INDEX_IMAGINARY]

    @property
    def real(self) -> np.ndarray:
        """ Returns the real component. """
        return self._array[Quaternion.INDEX_W]

    @property
    def is_identity(self) -> bool:
        """ Returns ``True`` if this quaternion is equal to :func:``Quaternion.identity``.

        Note: This does an epsilon float check. Is uses ``np_helpers.EPS_THRESHOLD`` as its default absolute tolerance.

        Returns:
            ``True`` if this quaternion is equal to identity, otherwise ``False``.

        """
        return np.allclose(self.array, np.asarray([0, 0, 0, 1], dtype=np.float32), atol=np_helpers.EPS_THRESHOLD)

    def square_norm(self) -> float:
        """ Calculates the squared L2 norm of this quaternion. """
        return float(np.sum(self._array**2))

    def norm(self) -> float:
        """ Calculates the L2 norm if this quaternion. """
        return math.sqrt(self.square_norm())

    @property
    def is_normalized(self) -> bool:
        """ Returns ``True`` if this quaternion  is normalized, i.e. has a norm of ``1.0``.

        Note: This does an epsilon float check. Is uses ``np_helpers.EPS_THRESHOLD`` as its default absolute tolerance.

        Returns:
            ``True`` if this quaternion has a norm if ``1.0``, otherwise ``False``.
        """
        return math.isclose(self.square_norm(), 1., abs_tol=np_helpers.EPS_THRESHOLD)

    def normalize(self) -> Self:
        """ Normalizes this quaternion.

        It makes sure that the result is always a normalized ``Quaternion`` instance.
        This means that ``result.is_normalized`` should always be ``True``.

        If the current quaternion is already normalized, this returns the same instance without change.
        If the current instance has a norm of ``0.0`` (or close to), an ``identity`` quaternion is returned.

        Returns:
            ``Quaternion`` object that is normalized.

        """
        norm = self.norm()

        if norm < np_helpers.EPS_THRESHOLD:  # Zero quaternion should normalize to identity
            return Quaternion.identity()

        if math.isclose(norm, 1., abs_tol=np_helpers.EPS_THRESHOLD):  # Already normalized quaternion should not change
            return self

        return self._new_instance(self.array / norm)

    def conjugate(self) -> Self:
        """ Calculates the conjugate of the current quaternion.

        A quaternion conjugate is a new quaternion with the same magnitude, but the sign of the imaginary parts changed.
        This in effect reverts the rotation axis.

        """
        arr = self._array.copy()
        arr[:3] *= -1
        return self._new_instance(arr)

    def reverse_axis(self) -> Self:
        """ Shortcut method for reversing the rotation axis of the current quaternion.

        Returns:
            ``Quaternion`` object with the same rotation angle, but reversed axis.
        """
        return self.conjugate()

    def reverse_angle(self) -> Self:
        """ Shortcut method for reversing the rotation angle of the current quaternion.

        Returns:
            ``Quaternion`` object with the same rotation axis, bit angle reversed.
        """
        arr = self._array.copy()
        arr[-1] *= -1
        return self._new_instance(arr)

    def invert(self) -> Self:
        """ Inverts the rotation of this quaternion.

        This also handles (potential) stretching in case the current quaternion was not normalized.
        That means that the following code should always be true:
        ``
            q = Quaternion([<some values>])
            q_inv = q.invert()

            assert (q * q_inv).is_identity
        ``

        Returns:
            ``Quaternion`` object that completely inverts the current rotation.
        """
        return self.conjugate() / self.square_norm()

    def __mul__(self, other: Union[Quaternion, float]) -> Self:
        """ Implements the multiplication (a * b) operator for ``Quaternion``.

        This accepts the following arguments:
         - ``Quaternion``: Compose this instance with ``other``. See :func:``~Quaternion.compose``.
         - ``float``: Scale the current instance with the given value. See :func:``~Quaternion.scale``.

        Args:
            other: ``Quaternion`` or ``float``, depending on the operation.

        Returns:
            ``Quaternion`` object with the respective operation applied.

        """
        if np.isscalar(other):
            return self.scale(float(other))

        if isinstance(other, Quaternion):
            return self.compose(other)

        raise TypeError(f"unsupported operand type(s) for *: 'Quaternion' and '{type(other)}'")

    def __truediv__(self, other: float) -> Self:
        """ Implements the (true) division operator (a / b) for ``Quaternion``.

        Contrary to :func:``~Quaternion.__mul__``, this only accepts ``float`` scalars.
        In that case, the current instance is inversely scaled by the given value

        Args:
            other: ``float`` scaling factor. See :func:``~Quaternion.scale``.

        Returns:
            ``Quaternion`` object with the inverse scaling operation applied.

        """
        if np.isscalar(other):
            return self.scale(1. / float(other))

        raise TypeError(f"unsupported operand type(s) for /: 'Quaternion' and '{type(other)}'")

    def scale(self, scalar: float):
        """ Scales the current quaternion.

        Note: This is _not_ a linear interpolation of the currently represented rotation.
        Instead, this is a simple vector multiplication on the underlying array.

        If ``scalar`` is close to ``1.0``, the same instance is returned.

        Args:
            scalar: A scaling factor.

        Returns:
            ``Quaternion`` object with all components scaled by the given factor.

        """
        if math.isclose(scalar, 1, abs_tol=np_helpers.EPS_THRESHOLD):
            return self
        return self._new_instance(self._array * scalar)

    def compose(self, other: Quaternion) -> Self:
        """ Composes, i.e. combines this quaternion with the given other one,

        If the current instance is an identity quaternion, the ``other`` instance is returned (unchanged).
        Similar, if ``other`` is an identity quaternion, the current instance is returned.

        Args:
            other: ``Quaternion`` object that should the composed with this one.

        Returns:
            ``Quaternion`` object that represents the composition of ``self`` and ``other``.

        """
        if self.is_identity:
            return other
        if other.is_identity:
            return self

        img_a = self.imaginary
        img_b = other.imaginary
        real_a = self.real
        real_b = other.real

        arr = np.empty((4,), dtype=np.float32)

        arr[Quaternion.INDEX_IMAGINARY] = real_a * img_b + real_b * img_a + np.cross(img_a, img_b)
        arr[Quaternion.INDEX_W] = real_a * real_b - np.dot(img_a, img_b)

        return self._new_instance(arr)

    @overload
    def get_axis_and_angle(self, *, degrees: bool = False) -> Tuple[np.ndarray, float]:
        pass

    @overload
    def get_axis_and_angle(self, *, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray], degrees: bool = False) -> Tuple[transform_helpers.TVector3LikeOrArray, float]:
        pass

    def get_axis_and_angle(self, *, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray] = None, degrees: bool = False) -> Tuple[transform_helpers.TVector3LikeOrArray, float]:
        """ Returns the rotation axis and angle of the current quaternion.

        The resulting angle is in radians if ``degrees`` is not given or ``False``.

        Args:
            vector_type_factory (optional): Factory callback for constructing the resulting axis vector. Defaults to :func:``~transform_helpers.default_vector_type_factory``.
            degrees (optional): ``True``, if the returned angle should be in degrees, otherwise ``False``. Defaults to ``False``.

        Returns:
            A tuple with (<axis>, <angle>) content.
        """
        if vector_type_factory is None:
            vector_type_factory = transform_helpers.default_vector_type_factory

        q = self.normalize()

        w = q.w
        if w > 1. and np_helpers.allclose(w, 1.) \
                or w < -1. and np_helpers.allclose(w, -1.):
            w = np_helpers.round_to_precision(q.w)
            
        angle = 2 * math.acos(w)
        s = math.sqrt(1 - w * w)

        if degrees:
            angle = np.rad2deg(angle)

        if np_helpers.allclose(s, 0.0):
            return vector_type_factory(q.imaginary), angle
        return vector_type_factory(q.imaginary / s), angle

    @overload
    def rotate(self, vector: Union[np.ndarray, Tuple[float, float, float], List[float]]) -> np.ndarray:
        pass

    @overload
    def rotate(self, vector: transform_helpers.TVector3LikeOrArray) -> transform_helpers.TVector3LikeOrArray:
        pass

    @overload
    def rotate(self, vector: Union[np.ndarray, Tuple[float, float, float], List[float]], *, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray]) -> transform_helpers.TVector3LikeOrArray:
        pass

    @overload
    def rotate(self, vector: transform_helpers.TVector3LikeOrArray, *, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray]) -> transform_helpers.TVector3LikeOrArray:
        pass

    def rotate(self, vector: AcceptedVector3Input, *, vector_type_factory: Callable[[np.ndarray], transform_helpers.TVector3LikeOrArray] = None) -> transform_helpers.TVector3LikeOrArray:
        """ Rotates the given vector.

        Args:
            vector: The vector to rotate. Accepts anything that is convertable to a 3-element vector using ``numpy.asarray``.
            vector_type_factory (optional): Factory callback for constructing the resulting vector.
                If ``vector`` is a subclass of ``Vector3Like``, this defaults to that classes constructor.
                Otherwise :func:``~transform_helpers.default_vector_type_factory`` is used.

        Returns:
            vector object (type depending on ``vector_type_factory``) containing ``vector`` rotated by this quaternion.

        """
        if vector_type_factory is None:
            if isinstance(vector, transform_helpers.Vector3Like):
                vector_type_factory = type(vector)
            else:
                vector_type_factory = transform_helpers.default_vector_type_factory

        v = np.asarray(vector, dtype=np.float32)

        matrix = self.to_matrix()

        result = np.einsum('jk,k->j', matrix, v)

        return vector_type_factory(result)

    @classmethod
    def average(cls, values: Sequence[Self], *, weights: Sequence[Union[float, int]] = None) -> Self:
        """ Averages the given sequence of ``Quaternion`` instances, optionally using weights.

        Args:
            values: A sequence of ``Quaternion`` objects that should be averaged.
            weights (optional): Weights for the ``values`` list. If not given, this defaults to equal weights for all.

        Returns:
            ``Quaternion`` object that represents the average rotation of all given ``values``.
        """
        if weights is None:
            weights = np.ones((len(values), ))
        elif len(weights) != len(values):
            raise ValueError("Weights argument must have same length as values.")

        A = np.zeros((4, 4), dtype=np.float64)

        w_sum = 0

        for q, w in zip(values, weights):
            A = w * np.outer(q.array, q.array) + A
            w_sum += w

        A /= w_sum

        eigen_values, eigen_vectors = np.linalg.eig(A)
        eigen_vectors = eigen_vectors[:, eigen_values.argsort()[::-1]]
        return cls(eigen_vectors[:, 0])

