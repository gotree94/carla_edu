import numpy as np
import cv2

SEG_COLORS = {
    0: (0, 0, 0),
    1: (70, 70, 70),
    2: (100, 40, 40),
    3: (55, 90, 80),
    4: (220, 20, 60),
    5: (153, 153, 153),
    6: (157, 234, 50),
    7: (128, 64, 128),
    8: (244, 35, 232),
    9: (107, 142, 35),
    10: (0, 0, 142),
    11: (102, 102, 156),
    12: (220, 220, 0),
    13: (70, 130, 180),
    14: (81, 0, 81),
    15: (150, 100, 100),
    16: (180, 165, 180),
    17: (250, 170, 30),
    18: (110, 190, 160),
    19: (170, 120, 50),
    20: (45, 60, 150),
    21: (145, 170, 100),
}

ROAD_LABELS = {6, 7, 8}
VEHICLE_LABEL = 10
PEDESTRIAN_LABEL = 4

FX = FY = 500.0
CX = 320.0
CY = 240.0


def colorize_segmentation(seg_map):
    h, w = seg_map.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)
    for cid, color in SEG_COLORS.items():
        mask = seg_map == cid
        out[mask] = color
    return out


def extract_road_mask(seg_map):
    mask = np.zeros_like(seg_map, dtype=bool)
    for label in ROAD_LABELS:
        mask |= (seg_map == label)
    return mask


def extract_vehicles(seg_map):
    return seg_map == VEHICLE_LABEL


def extract_pedestrians(seg_map):
    return seg_map == PEDESTRIAN_LABEL


def depth_to_pointcloud(depth_map):
    h, w = depth_map.shape
    u, v = np.meshgrid(np.arange(w), np.arange(h))
    z = depth_map / 1000.0
    x = (u - CX) * z / FX
    y = (v - CY) * z / FY
    points = np.stack([x, y, z], axis=-1)
    return points.reshape(-1, 3)


def compute_obstacle_distances(depth_map, seg_map):
    vehicle_mask = extract_vehicles(seg_map)
    pedestrian_mask = extract_pedestrians(seg_map)
    any_obstacle = vehicle_mask | pedestrian_mask

    if not any_obstacle.any():
        return None, None

    obstacle_depths = depth_map[any_obstacle]
    min_vehicle_dist = float('inf')
    min_pedestrian_dist = float('inf')

    if vehicle_mask.any():
        min_vehicle_dist = np.min(depth_map[vehicle_mask])

    if pedestrian_mask.any():
        min_pedestrian_dist = np.min(depth_map[pedestrian_mask])

    return min_vehicle_dist, min_pedestrian_dist


def detect_lanes(seg_map):
    road_mask = extract_road_mask(seg_map)

    road_uint8 = (road_mask * 255).astype(np.uint8)
    edges = cv2.Canny(road_uint8, 50, 150)

    h, w = seg_map.shape
    bottom_half = edges[h//2:, :]

    lines = cv2.HoughLinesP(
        bottom_half,
        rho=1,
        theta=np.pi/180,
        threshold=50,
        minLineLength=30,
        maxLineGap=10
    )

    return lines
