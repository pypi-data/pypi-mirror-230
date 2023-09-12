from typing import Union, Tuple, List, Collection, Sequence, Iterable

import numpy as np
from typing_extensions import Self

from asl_utility import transform_helpers, np_helpers


class JointPose(transform_helpers.ArrayLike):

    @classmethod
    def zero(cls, joint_names: Collection[str]) -> Self:
        return cls(joint_names, np.zeros(len(joint_names), dtype=np.float32))

    def __init__(self, joint_names: Collection[str], values: Union[np.ndarray, transform_helpers.ArrayLike, List[float]]):
        values = np.asarray(values)

        assert values.shape == (len(joint_names),), f"JointPose must be a {len(joint_names)} element vector, but got {values.shape[0]} dims."

        if values.dtype != np.float32:
            values = values.astype(np.float32)

        if values.base is not None:
            values = np.copy(values)

        values.flags.writeable = False
        self._values = values

        self._joint_names = tuple(joint_names)

    @property
    def joint_names(self) -> Sequence[str]:
        return self._joint_names

    @property
    def array(self) -> np.ndarray:
        return self._values

    @property
    def is_zero(self) -> bool:
        return np.allclose(self.array, np.zeros(len(self.joint_names), dtype=np.float32), atol=np_helpers.EPS_THRESHOLD)

    def filter(self, desired_joints: Sequence[str], ignore_missing: bool = False) -> Self:
        desired_joints = tuple(desired_joints)
        if desired_joints == self.joint_names:
            return self

        indices = [self.joint_names.index(j) for j in desired_joints if j in self.joint_names or not ignore_missing]
        return transform_helpers.JointPose(desired_joints, self.array[indices])
