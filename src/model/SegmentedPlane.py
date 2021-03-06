import numpy as np

from src.utils.colors import get_random_color, normalize_color


class SegmentedPlane:

    NO_TRACK = -1

    def __init__(self, pcd_indices: np.array, zero_depth_pcd_indices: np.array, track_id: int, color=None):
        self.pcd_indices = pcd_indices
        self.track_id = track_id
        self.zero_depth_pcd_indices = zero_depth_pcd_indices
        if color is None:
            color = get_random_color()
        self.color = color
        self.normalized_color = normalize_color(self.color)

    def set_color(self, color):
        self.color = color
        self.normalized_color = normalize_color(self.color)

    def __repr__(self):
        return "Plane: {{pcd_indices: {0}, color: {1}, track_id: {2}}}".format(self.pcd_indices, self.color, self.track_id)
