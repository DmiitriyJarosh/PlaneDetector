import cv2
import numpy as np
import open3d as o3d
import OutlierDetector

from CVATAnnotation import CVATAnnotation
from src.detectors import AnnotationsDetector
from src.parser import create_input_parser, loaders, algos, metrics
from src.utils.point_cloud import depth_to_pcd


def load_annotations(loader, depth_frame_num, path_to_annotations, filter_outliers):
    frame_number = loader.depth_to_rgb_index[depth_frame_num]
    annotation = CVATAnnotation(path_to_annotations)
    result_pcd = AnnotationsDetector.segment_pcd_from_depth_by_annotations(
        depth_image,
        cam_intrinsic,
        initial_pcd_transform,
        annotation,
        frame_number
    )
    if filter_outliers:
        result_pcd = OutlierDetector.remove_planes_outliers(result_pcd)

    return result_pcd


if __name__ == '__main__':
    parser = create_input_parser()
    args = parser.parse_args()
    path_to_dataset = args.dataset_path
    depth_frame_num = args.frame_num
    loader_name = args.loader

    loader = loaders[loader_name](path_to_dataset)
    depth_image_path = loader.depth_images[depth_frame_num]

    depth_image = cv2.imread(depth_image_path, cv2.IMREAD_GRAYSCALE)
    result_pcd = None
    detected_pcd = None
    image_shape = depth_image.shape
    cam_intrinsic = loader.config.get_cam_intrinsic(image_shape)
    initial_pcd_transform = loader.config.get_initial_pcd_transform()

    if args.annotations_path is not None:
        result_pcd = load_annotations(loader, depth_frame_num, args.annotations_path, args.filter_annotation_outliers)
        o3d.visualization.draw_geometries([result_pcd.get_color_pcd_for_visualization()])

    if args.algo is not None:
        pcd = depth_to_pcd(o3d.io.read_image(depth_image_path), cam_intrinsic, initial_pcd_transform)
        detector = algos[args.algo]
        detected_pcd = detector.detect_planes(pcd)
        o3d.visualization.draw_geometries([detected_pcd.get_color_pcd_for_visualization()])

    if args.annotations_path is not None and args.algo is not None and len(args.metric) > 0:
        for metric_name in args.metric:
            benchmark = metrics[metric_name]()
            benchmark_result = benchmark.execute(detected_pcd, result_pcd)
            print(benchmark_result)
