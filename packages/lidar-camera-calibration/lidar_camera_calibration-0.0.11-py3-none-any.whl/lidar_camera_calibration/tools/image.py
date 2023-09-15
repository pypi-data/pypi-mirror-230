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

from typing import Tuple

import numpy as np

from lidar_camera_calibration.tools.timestamp_np import TimeStamp

try:
    from rosbags.typesys.types import sensor_msgs__msg__Image as Image
except ImportError as e:
    raise ImportError(
        'rosbags library not installed, run "pip install -U rosbags"'
    ) from e


def read_image(msg: Image) -> Tuple[np.ndarray, TimeStamp]:
    time = TimeStamp(msg.header.stamp.sec, msg.header.stamp.nanosec)

    if msg.encoding == "mono8":
        image = np.ndarray(
            shape=(msg.height, msg.width),
            dtype=np.uint8,
            buffer=msg.data,
        )
        return image, time
    else:
        raise TypeError(f"[ERROR] Unknown image encoding {msg.encoding}")
