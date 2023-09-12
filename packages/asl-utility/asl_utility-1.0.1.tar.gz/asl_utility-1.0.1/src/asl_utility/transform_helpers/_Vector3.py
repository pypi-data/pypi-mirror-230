import math
from typing import Union, Tuple, List

import numpy as np
from typing_extensions import Self

from asl_utility import transform_helpers, np_helpers


AcceptedVector3Input = Union[np.ndarray, transform_helpers.Vector3Like, Tuple[float, float, float], List[float]]


class Vector3(transform_helpers.Vector3Like):
    """ Vector3 class representing a 3d cartesian position/translation/offset in (x, y, z) notation.

    Note: This class is immutable. This means the underlying numpy array is made read-only.
    And each operation that would manipulate its content instead returns a new instance.

    Libraries might derive from this class to add special behavior or extra/additional information.
    To do this, one must override the constructor as well as ``_new_instance()`` method.

    """

    @classmethod
    def identity(cls) -> Self:
        """ Returns an identity vector, i.e. one that does not apply any translation.

        Adding other vectors with this should result in the same original.
        ``
            v = Vector3([<some values>])

            i = Vector3.identity()

            r = v + i

            assert v == r  # Technically, this should be a proper semantic equality test. Bit it gets the point across...
        ``
        """
        return cls(np.zeros(shape=(3,), dtype=np.float32))

    @classmethod
    def one(cls) -> Self:
        """ Returns a ``Vector3`` object with all components set to ``1.0``. """
        return cls(np.ones(shape=(3,), dtype=np.float32))

    @classmethod
    def from_values(cls, x: float, y: float, z: float) -> Self:
        """ Creates a ``Vector3`` object from the given three float values. """
        return cls(np.asarray([x, y, z]))

    def __init__(self, array: AcceptedVector3Input) -> None:
        """ Creates a vector from the given raw array.

        This must be a 3-element array, or something directly convertible using ``numpy.asarray``.
        The array is then made read-only. If a view is given, a copy will be made first.

        Args:
            array: A 3-element numpy array or somthing convertible.
        """
        array = np.asarray(array)

        assert array.shape == (3,), "Vector3 must be a three element vector."

        if array.dtype != np.float32:
            array = array.astype(np.float32)

        if array.base is not None:
            array = np.copy(array)

        array.flags.writeable = False
        self._array = array

    def _new_instance(self, array: np.ndarray) -> Self:
        return type(self)(array)

    def __str__(self):
        """ Converts the vector to a readable string representation. """
        return f'V{("(Z)" if self.is_identity else "")}{str(self.array)}'

    def __repr__(self):
        """ Converts the quaternion to a readable string representation. Same as :func:``~Vector3.__str__``. """
        return str(self)

    @property
    def array(self) -> np.ndarray:
        """ Returns the underlying array for direct numpy access & processing. """
        return self._array

    @property
    def is_identity(self) -> bool:
        """ Returns ``True`` if this vector is equal to :func:``Vector3.identity``.

        Note: This does an epsilon float check. Is uses ``np_helpers.EPS_THRESHOLD`` as its default absolute tolerance.

        Returns:
            ``True`` if this vector is equal to identity, otherwise ``False``.

        """
        return np.allclose(self.array, np.asarray([0, 0, 0], dtype=np.float32), atol=np_helpers.EPS_THRESHOLD)

    def square_norm(self) -> float:
        """ Calculates the squared L2 norm of this quaternion. """
        return float(np.sum(self._array**2))

    def norm(self) -> float:
        """ Calculates the L2 norm if this quaternion. """
        return math.sqrt(self.square_norm())

    @property
    def is_normalized(self) -> bool:
        """ Returns ``True`` if this vector is normalized, i.e. has a norm of ``1.0``.

        Note: This does an epsilon float check. Is uses ``np_helpers.EPS_THRESHOLD`` as its default absolute tolerance.

        Returns:
            ``True`` if this vector has a norm if ``1.0``, otherwise ``False``.
        """
        return math.isclose(self.square_norm(), 1., abs_tol=np_helpers.EPS_THRESHOLD)

    def normalize(self) -> Self:
        """ Normalizes this vector.

        It makes sure that the result is always a normalized ``Vector3`` instance.
        This means that ``result.is_normalized`` should always be ``True``.

        If the current vector is already normalized, this returns the same instance without change.

        Returns:
            ``Vector3`` object that is normalized.

        Raises:
            ValueError: If the current vector has a norm of ``0.0``, i.e. ``self.is_normalized == True``.
                Unfortunately, there exists no "default" ``Vector3`` value which is normalized (``Vector3.identity`` has norm of ``0.0``).
                So we can't return a semantic meaningful value in case the current one is not normalizable, thus the exception.

        """
        norm = self.norm()

        if norm < np_helpers.EPS_THRESHOLD:
            raise ValueError("Can't normalize a zero (identity) vector.")

        if math.isclose(norm, 1., abs_tol=np_helpers.EPS_THRESHOLD):  # Already normalized quaternion should not change
            return self

        return self._new_instance(self.array / norm)

    def __add__(self, other: AcceptedVector3Input) -> Self:
        """ Implements the addition (a + b) operator for ``Vector3``.

        Args:
            other: Anything that is acceptable as a 3-element vector.

        Returns:
            ``Vector3`` object representing the addition if ``self`` with ``other``. See :func::``Vector3.add``.

        Raises:
            TypeError: ``other`` could not be converted to a 3-element vector,

        """
        try:
            a = np.asarray(other, dtype=float)
            if a.shape == (3,):
                return self.add(a)
        except ValueError:
            pass

        raise TypeError(f"unsupported operand type(s) for +: 'Vector3' and '{type(other)}'")

    def __sub__(self, other: AcceptedVector3Input) -> Self:
        """ Implements the subtraction (a - b) operator for ``Vector3``.

        Args:
            other: Anything that is acceptable as a 3-element vector.

        Returns:
            ``Vector3`` object representing the addition if ``self`` with ``other``. See :func::``Vector3.subtract``.

        Raises:
            TypeError: ``other`` could not be converted to a 3-element vector,

        """
        try:
            a = np.asarray(other, dtype=float)
            if a.shape == (3,):
                return self.subtract(a)
        except ValueError:
            pass

        raise TypeError(f"unsupported operand type(s) for -: 'Vector3' and '{type(other)}'")

    def __neg__(self) -> Self:
        """ Implements the inversion (-a) operator for ``Vector3``. See :func:``Vector3.invert``."""

        return self.invert()

    def __mul__(self, other: Union[float, int, AcceptedVector3Input]) -> Self:
        """ Implements the multiplication (a * b) operator for ``Vector3``.

        This accepts the following arguments:
         - ``Vector3`` or similar: Elementwise multiply this vector with the other. See :func:``Vector3.elementwise_multiply``.
         - ``float`` or similar: Scale the current instance with the given value. See :func:``~Vecto3.scale``.

        Args:
            other: vector-like or scalar, depending on the operation.

        Returns:
            ``Vector3`` object with the respective operation applied.

        """
        if np.isscalar(other):
            try:
                other_as_float = float(other)
                return self.scale(other_as_float)
            except ValueError:
                pass

        try:
            a = np.asarray(other, dtype=float)
            if a.shape == (3,):
                return self.elementwise_multiply(a)
        except ValueError:
            pass

        raise TypeError(f"unsupported operand type(s) for *: 'Vector3' and '{type(other)}'")

    def __truediv__(self, other: Union[float, int]) -> Self:
        """ Implements the (true) division (a / b) operator for ``Vector3``.

        This accepts the following arguments:
         - ``float`` or similar: Scale the current instance with the given value. See :func:``~Vecto3.scale``.

        Args:
            other: scalar to divide the current vector by.

        Returns:
            ``Vector3`` object with the respective operation applied.

        """
        if np.isscalar(other):
            try:
                other_as_float = float(other)
                return self.scale(1. / other_as_float)
            except ValueError:
                pass

        raise TypeError(f"unsupported operand type(s) for *: 'Vector3' and '{type(other)}'")

    def scale(self, scalar: Union[float, int]) -> Self:
        """ Scales the current vector.

        If ``scalar`` is close to ``1.0``, the same instance is returned.

        Args:This is essentially the same as
            scalar: A scaling factor.

        Returns:
            ``Vector3`` object with all components scaled by the given factor.

        """
        if math.isclose(scalar, 1, abs_tol=np_helpers.EPS_THRESHOLD):
            return self
        return self._new_instance(self._array * scalar)

    def invert(self) -> Self:
        """ Inverts the current vector, i.e. all elements negated. """
        return self.scale(-1)

    def elementwise_multiply(self, scalar: AcceptedVector3Input) -> Self:
        """ Applies element-wise multiplication.

        This is essentially the same as ``Vector3([self.x * scalar.x, self.y * scalar.y, self.z * scalar.z])``.

        If all elements in ``scalar`` are close to ``1.0``, this returns ``self`` unchanged.

        Args:
            scalar: Anything that is acceptable as a 3-element vector.

        Returns:
            ``Vector3`` object with each element multiplied with the respective element from ``scalar``.
        """
        scalar = np.asarray(scalar)
        if np_helpers.allclose(scalar, 1):
            return self
        return self._new_instance(self.array * scalar)

    def add(self, other: AcceptedVector3Input) -> Self:
        """ Adds the current and the given vector.

        If all elements in ``other`` are close to ``0.0``, this returns ``self`` unchanged.

        Args:
            other: Anything that is acceptable as a 3-element vector.

        Returns:
            ``Vector3`` object with each element added with the respective element from ``other``.

        """
        other = np.asarray(other)
        if np_helpers.allclose(other, 0):
            return self
        return self._new_instance(self.array + other)

    def subtract(self, other: Union[np.ndarray, transform_helpers.Vector3Like, Tuple[float, float, float], List[float]]) -> Self:
        """ Subtracts other from the current vector.

        If all elements in ``other`` are close to ``0.0``, this returns ``self`` unchanged.

        Args:
            other: Anything that is acceptable as a 3-element vector.

        Returns:
            ``Vector3`` object with each element of ``other`` subtracted from the respective element in ``self``.

        """
        return self.add(-np.asarray(other))

