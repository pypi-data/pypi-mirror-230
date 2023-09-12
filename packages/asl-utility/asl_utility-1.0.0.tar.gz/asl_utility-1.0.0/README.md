# ASL Utility


This is a utility library mostly concerned with Numpy and spactial transformation helpers.

The main component is the `asl_utility.transform` package. This contains multiple classes concerned with rotation, 
transformation & translation. 

 - `Vector3`: 3d translation, offset or position in cartesian space
 - `Quaternion`: 3d rotation and orientation in cartesian space
 - `Transformaton`: 3d transformation (translate, rotate & scale) in cartesian space.

Furthermore, it has some interface and data holder classes to support these main components. 
Check the module and class documnentation for more details.


## Installation

This library is available on PyPi.
```
pip install asl-utility
```


## Example usage
```python
import numpy as np
from asl_utility import transform_helpers

rot1 = transform_helpers.Quaternion.from_axis_and_angle((1, 0, 0), np.pi/4)  # 45° around x-axis
rot2 = transform_helpers.Quaternion.from_euler("XYZ", [0, 0, 30], degrees=True)

rotation = rot1 * rot2 
translation = transform_helpers.Vector3([42, 13, 37])

camera_to_world = transform_helpers.Transformation.from_translation_and_rotation(translation, rotation)
world_to_camera = camera_to_world.invert()

pos_in_cam = np.asarray([10, 20, 30])

pos_in_world = camera_to_world.apply_vector(pos_in_cam)
pos_in_cam2 = world_to_camera.apply_vector(pos_in_world)
```


