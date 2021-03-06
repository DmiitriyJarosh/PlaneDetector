import os
from abc import abstractmethod

import cv2
import numpy as np

from src.loaders.BaseLoader import BaseLoader

from src.loaders.depth_image.CameraConfig import CameraConfig
from src.model.SegmentedPointCloud import SegmentedPointCloud
from src.utils.point_cloud import depth_to_pcd_custom


class ImageLoader(BaseLoader):
    def __init__(self, path):
        super().__init__(path)
        self.config = self._provide_config()

        rgb_path, depth_path = self._provide_rgb_and_depth_path(path)

        rgb_filenames, depth_filenames = self._provide_filenames(rgb_path, depth_path)

        self.depth_images = [os.path.join(depth_path, filename) for filename in depth_filenames]
        self.rgb_images = [os.path.join(rgb_path, filename) for filename in rgb_filenames]
        self.depth_to_rgb_index = self._match_rgb_with_depth(rgb_filenames, depth_filenames)

    def get_frame_count(self) -> int:
        return len(self.depth_images)

    @abstractmethod
    def _provide_config(self) -> CameraConfig:
        pass

    @abstractmethod
    def _provide_rgb_and_depth_path(self, path: str) -> (str, str):
        pass

    @abstractmethod
    def _match_rgb_with_depth(self, rgb_filenames, depth_filenames) -> list:
        pass

    @abstractmethod
    def _provide_filenames(self, rgb_path, depth_path) -> (list, list):
        pass

    def read_depth_image(self, frame_num) -> np.array:
        depth_frame_path = self.depth_images[frame_num]
        return cv2.imread(depth_frame_path, cv2.IMREAD_ANYDEPTH)

    def read_pcd(self, frame_num) -> SegmentedPointCloud:
        depth_image = self.read_depth_image(frame_num)
        cam_intrinsics = self.config.get_cam_intrinsic(depth_image.shape)
        initial_pcd_transform = self.config.get_initial_pcd_transform()

        pcd, zero_depth_indices = depth_to_pcd_custom(depth_image, cam_intrinsics, initial_pcd_transform)

        return SegmentedPointCloud(
            pcd=pcd,
            unsegmented_cloud_indices=np.arange(depth_image.size),
            zero_depth_cloud_indices=zero_depth_indices,
            structured_shape=(depth_image.shape[0], depth_image.shape[1])
        )
