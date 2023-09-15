# MIT License
#
# Copyright (c) 2022 Ignacio Vizzo, Tiziano Guadagnino, Benedikt Mersch, Cyrill
# Stachniss.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import sys
from pathlib import Path
from typing import Sequence

import natsort


class RosbagDataset:
    def __init__(
        self,
        data_dir: Sequence[Path],
        topic: str,
        cmd_line_arg: str,
        ros_msg_type: str,
        *_,
        **__,
    ):
        """ROS1 / ROS2 bagfile dataloader.

        It can take either one ROS2 bag file or one or more ROS1 bag files belonging to a split bag.
        The reader will replay ROS1 split bags in correct timestamp order.

        """
        try:
            from rosbags.highlevel import AnyReader
        except ModuleNotFoundError:
            print('rosbags library not installed, run "pip install -U rosbags"')
            sys.exit(1)
        if data_dir is None:
            print(
                "[ERROR] The data_dir argument is of type None. Expecting data_dir to be a Path or List[Path] object."
            )
            sys.exit(1)

        # FIXME: This is quite hacky, trying to guess if we have multiple .bag, one or a dir
        if isinstance(data_dir, Path):
            self.sequence_id = os.path.basename(data_dir).split(".")[0]
            self.bag = AnyReader([data_dir])
        else:
            self.sequence_id = os.path.basename(data_dir[0]).split(".")[0]
            self.bag = AnyReader(data_dir)
            print("Reading multiple .bag files in directory:")
            print("\n".join(natsort.natsorted([path.name for path in self.bag.paths])))
        self.bag.open()
        self.cmd_line_arg = cmd_line_arg
        self.ros_msg_type = ros_msg_type
        self.topic = self.check_topic(topic)
        self.n_scans = self.bag.topics[self.topic].msgcount

        # limit connections to selected topic
        connections = [x for x in self.bag.connections if x.topic == self.topic]
        self.msgs = self.bag.messages(connections=connections)
        self.timestamps = []

    def __del__(self):
        if hasattr(self, "bag"):
            self.bag.close()

    def __len__(self):
        return self.n_scans

    def __getitem__(self, idx):
        connection, timestamp, rawdata = next(self.msgs)
        self.timestamps.append(self.to_sec(timestamp))
        msg = self.bag.deserialize(rawdata, connection.msgtype)
        return msg

    @staticmethod
    def to_sec(nsec: int):
        return float(nsec) / 1e9

    def get_frames_timestamps(self) -> list:
        return self.timestamps

    def check_topic(self, topic: str) -> str:
        # Extract all PointCloud2 msg topics from the bagfile
        topics = [
            topic[0]
            for topic in self.bag.topics.items()
            if topic[1].msgtype == self.ros_msg_type
        ]

        def print_available_topics_and_exit():
            print(50 * "-")
            for t in topics:
                print(f"--{self.cmd_line_arg} {t}")
            print(50 * "-")
            sys.exit(1)

        if topic is None and topic not in topics:
            print(
                "[ERROR] topic is None. "
                f"Please select one of the following topics with the --{self.cmd_line_arg} flag"
            )
            print_available_topics_and_exit()

        if topic and topic in topics:
            return topic
        # when user specified the topic check that exists
        if topic and topic not in topics:
            print(
                f'[ERROR] Dataset does not contain any msg with the topic name "{topic}". '
                f"Please select one of the following topics with the --{self.cmd_line_arg} flag"
            )
            print_available_topics_and_exit()

        if len(topics) > 1:
            print(
                f"Multiple {self.ros_msg_type} topics available. "
                f"Please select one of the following topics with the --{self.cmd_line_arg} flag"
            )
            print_available_topics_and_exit()

        if len(topics) == 0:
            print(
                f"[ERROR] Your dataset does not contain any {self.ros_msg_type} topic"
            )
        if len(topics) == 1:
            return topics[0]
