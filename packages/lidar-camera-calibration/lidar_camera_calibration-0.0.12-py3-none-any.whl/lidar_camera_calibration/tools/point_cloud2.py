# Copyright 2008 Willow Garage, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the Willow Garage, Inc. nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
This file is based on https://github.com/ros2/common_interfaces/blob/4bac182a0a582b5e6b784d9fa9f0dabc1aca4d35/sensor_msgs_py/sensor_msgs_py/point_cloud2.py
All rights reserved to the original authors: Tim Field and Florian Vahl.
"""

import sys
from typing import Iterable, List, Optional, Tuple

import numpy as np

from lidar_camera_calibration.tools.timestamp_np import TimeStamp

try:
    from rosbags.typesys.types import sensor_msgs__msg__PointCloud2 as PointCloud2
    from rosbags.typesys.types import sensor_msgs__msg__PointField as PointField
except ImportError as e:
    raise ImportError(
        'rosbags library not installed, run "pip install -U rosbags"'
    ) from e


_DATATYPES = {}
_DATATYPES[PointField.INT8] = np.dtype(np.int8)
_DATATYPES[PointField.UINT8] = np.dtype(np.uint8)
_DATATYPES[PointField.INT16] = np.dtype(np.int16)
_DATATYPES[PointField.UINT16] = np.dtype(np.uint16)
_DATATYPES[PointField.INT32] = np.dtype(np.int32)
_DATATYPES[PointField.UINT32] = np.dtype(np.uint32)
_DATATYPES[PointField.FLOAT32] = np.dtype(np.float32)
_DATATYPES[PointField.FLOAT64] = np.dtype(np.float64)

DUMMY_FIELD_PREFIX = "unnamed_field"


def read_point_cloud(
    msg: PointCloud2, read_intensity: bool = False, use_per_point_timestamp: bool = False
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract points and timestamps from a PointCloud2 message.

    :return: Tuple of [points, timestamps]
        points: array of x, y, z points, shape: (N, 3) or (N,4) if intensity is returned
        timestamps: array of per-pixel timestamps, shape: (N,)
    """

    field_names = ["x", "y", "z"]
    time = TimeStamp(msg.header.stamp.sec, msg.header.stamp.nanosec)
    fields_str = ", ".join([field.name for field in msg.fields])

    # Get intensity field
    intensity_field = None
    if read_intensity:
        for field in msg.fields:
            if field.name in ["I", "intensity"]:
                intensity_field = field.name
                field_names.append(intensity_field)
                break
        if intensity_field is None:
            raise ValueError(
                f"No intensity field in msg field data. Fields are {fields_str}"
            )
    # Get time field
    t_field = None
    for field in msg.fields:
        if field.name in ["t", "timestamp", "time"]:
            t_field = field.name
            field_names.append(t_field)
            break

    points_structured = read_points(msg, field_names=field_names)

    if intensity_field is None:
        points = np.column_stack(
            [points_structured["x"], points_structured["y"], points_structured["z"]]
        )
    else:
        points = np.column_stack(
            [
                points_structured["x"],
                points_structured["y"],
                points_structured["z"],
                points_structured[intensity_field],
            ]
        )
    # Remove nan if any
    idx_keep = ~np.any(np.isnan(points), axis=1)
    nkeep = idx_keep.sum()
    npoints = idx_keep.size
    if nkeep != npoints:
        print(
            f"[WARNING] {npoints-nkeep} of {npoints} points are being discarded as nans have been detected!"
        )
    points = points[idx_keep]

    if use_per_point_timestamp:
        if t_field:
            timestamps = points_structured[t_field].astype(np.int32)
            timestamps = timestamps[idx_keep]
            timestamps = TimeStamp(nsec=timestamps) + time
        else:
            timestamps = TimeStamp(
                np.array(
                    [
                        time,
                    ]
                ).repeat(nkeep)
            )
        return points.astype(np.float64), timestamps
    else:
        return points.astype(np.float64), time


def read_points(
    cloud: PointCloud2,
    field_names: Optional[List[str]] = None,
    uvs: Optional[Iterable] = None,
    reshape_organized_cloud: bool = False,
) -> np.ndarray:
    """
    Read points from a sensor_msgs.PointCloud2 message.
    :param cloud: The point cloud to read from sensor_msgs.PointCloud2.
    :param field_names: The names of fields to read. If None, read all fields.
                        (Type: Iterable, Default: None)
    :param uvs: If specified, then only return the points at the given
        coordinates. (Type: Iterable, Default: None)
    :param reshape_organized_cloud: Returns the array as an 2D organized point cloud if set.
    :return: Structured NumPy array containing all points.
    """
    # Cast bytes to numpy array
    points = np.ndarray(
        shape=(cloud.width * cloud.height,),
        dtype=dtype_from_fields(cloud.fields, point_step=cloud.point_step),
        buffer=cloud.data,
    )

    # Keep only the requested fields
    if field_names is not None:
        assert all(
            field_name in points.dtype.names for field_name in field_names
        ), "Requests field is not in the fields of the PointCloud!"
        # Mask fields
        points = points[list(field_names)]

    # Swap array if byte order does not match
    if bool(sys.byteorder != "little") != bool(cloud.is_bigendian):
        points = points.byteswap(inplace=True)

    # Select points indexed by the uvs field
    if uvs is not None:
        # Don't convert to numpy array if it is already one
        if not isinstance(uvs, np.ndarray):
            uvs = np.fromiter(uvs, int)
        # Index requested points
        points = points[uvs]

    # Cast into 2d array if cloud is 'organized'
    if reshape_organized_cloud and cloud.height > 1:
        points = points.reshape(cloud.width, cloud.height)

    return points


def dtype_from_fields(
    fields: Iterable[PointField], point_step: Optional[int] = None
) -> np.dtype:
    """
    Convert a Iterable of sensor_msgs.msg.PointField messages to a np.dtype.
    :param fields: The point cloud fields.
                   (Type: iterable of sensor_msgs.msg.PointField)
    :param point_step: Point step size in bytes. Calculated from the given fields by default.
                       (Type: optional of integer)
    :returns: NumPy datatype
    """
    # Create a lists containing the names, offsets and datatypes of all fields
    field_names = []
    field_offsets = []
    field_datatypes = []
    for i, field in enumerate(fields):
        # Datatype as numpy datatype
        datatype = _DATATYPES[field.datatype]
        # Name field
        if field.name == "":
            name = f"{DUMMY_FIELD_PREFIX}_{i}"
        else:
            name = field.name
        # Handle fields with count > 1 by creating subfields with a suffix consiting
        # of "_" followed by the subfield counter [0 -> (count - 1)]
        assert field.count > 0, "Can't process fields with count = 0."
        for a in range(field.count):
            # Add suffix if we have multiple subfields
            if field.count > 1:
                subfield_name = f"{name}_{a}"
            else:
                subfield_name = name
            assert (
                subfield_name not in field_names
            ), "Duplicate field names are not allowed!"
            field_names.append(subfield_name)
            # Create new offset that includes subfields
            field_offsets.append(field.offset + a * datatype.itemsize)
            field_datatypes.append(datatype.str)

    # Create dtype
    dtype_dict = {
        "names": field_names,
        "formats": field_datatypes,
        "offsets": field_offsets,
    }
    if point_step is not None:
        dtype_dict["itemsize"] = point_step
    return np.dtype(dtype_dict)
