import carla
import time
import cv2
import numpy as np
from datetime import datetime

from config import CARLA_HOST, CARLA_PORT, CARLA_TIMEOUT, SAVE_DIR, LOG_DIR
from sensors import SensorSuite
from perception import (colorize_segmentation, compute_obstacle_distances,
                        detect_lanes, depth_to_pointcloud)
from slam import SimpleVisualSLAM
from controller import VehicleController
from utils import (ensure_dir, make_spectator_follow, create_route,
                   get_vehicle_speed)


def main():
    client = carla.Client(CARLA_HOST, CARLA_PORT)
    client.set_timeout(CARLA_TIMEOUT)
    world = client.get_world()
    bp_lib = world.get_blueprint_library()
    map = world.get_map()

    vehicle_bp = bp_lib.find('vehicle.tesla.model3')
    start_pose = map.get_spawn_points()[50]
    vehicle = world.spawn_actor(vehicle_bp, start_pose)
    print(f"Vehicle spawned at {start_pose.location}")

    sensors = SensorSuite(world, vehicle)
    sensors.setup_all_cameras()
    print(f"8 x (RGB + Seg + Depth) = 24 sensors initialized")

    controller = VehicleController(vehicle)
    slam = SimpleVisualSLAM()

    route = create_route(world, start_pose.location,
                         num_waypoints=300, step=2.0)
    print(f"Route created: {len(route)} waypoints")

    spectator = world.get_spectator()
    save_dir = ensure_dir(SAVE_DIR)

    wp_idx = 0
    frame = 0
    running = True

    try:
        while running and wp_idx < len(route):
            target = route[wp_idx]
            vehicle_loc = vehicle.get_location()
            dist = vehicle_loc.distance(target.transform.location)

            if dist < 2.0:
                wp_idx += 1
                if wp_idx >= len(route):
                    break
                target = route[wp_idx]

            controller.follow_waypoint(target.transform.location)

            make_spectator_follow(spectator, vehicle)

            front_key = next(
                (k for k in sensors.data if 'Front Center_rgb' in k),
                None
            )

            if front_key and sensors.data[front_key] is not None:
                rgb = sensors.data[front_key]

                seg_key = front_key.replace('_rgb', '_seg')
                depth_key = front_key.replace('_rgb', '_depth')

                if seg_key in sensors.data and sensors.data[seg_key] is not None:
                    seg = sensors.data[seg_key]
                    seg_vis = colorize_segmentation(seg)
                    obstacle_dists = compute_obstacle_distances(
                        sensors.data.get(depth_key, np.zeros((480, 640))),
                        seg
                    )
                else:
                    seg_vis = np.zeros_like(rgb)
                    obstacle_dists = (None, None)

                if depth_key in sensors.data and sensors.data[depth_key] is not None:
                    depth = sensors.data[depth_key]
                    depth_norm = (depth / np.max(depth) * 255).astype(np.uint8)
                    depth_vis = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)
                else:
                    depth_vis = np.zeros_like(rgb)

                slam_result = slam.process_frame(rgb, timestamp=frame * 0.05)

                speed = get_vehicle_speed(vehicle)

                if obstacle_dists[0] is not None and obstacle_dists[0] < 5000:
                    controller.target_speed = 15.0
                else:
                    controller.target_speed = 30.0

                if frame % 30 == 0:
                    traj = slam.get_trajectory()
                    print(
                        f"Frame:{frame:5d} "
                        f"WP[{wp_idx:3d}/{len(route)}] "
                        f"Speed:{speed:5.1f}km/h "
                        f"SLAM Trajectory pts:{len(traj)} "
                        f"Features:{len(slam_result['keypoints'] or [])} "
                        f"Tracked:{slam_result['tracked']}"
                    )

                if frame % 10 == 0:
                    display = np.vstack([
                        np.hstack([rgb, seg_vis]),
                        np.hstack([depth_vis, slam_result['features_img']])
                    ])
                    display = cv2.resize(display, (960, 720))
                    cv2.imshow('CARLA Autonomous System', display)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        running = False
                        break

            frame += 1
            time.sleep(0.05)

        print(f"\nSimulation complete: {frame} frames, "
              f"{wp_idx}/{len(route)} waypoints traversed")

    finally:
        cv2.destroyAllWindows()
        sensors.destroy_all()
        vehicle.destroy()
        print("Cleanup complete")


if __name__ == '__main__':
    main()
