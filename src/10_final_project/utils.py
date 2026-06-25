import os
import json
import cv2
import numpy as np
from datetime import datetime


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path


def save_sensor_data(save_dir, rgb, seg, depth, metadata, frame_id):
    base = ensure_dir(os.path.join(save_dir, f'frame_{frame_id:06d}'))

    cv2.imwrite(os.path.join(base, 'rgb.png'),
                cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    np.save(os.path.join(base, 'seg.npy'), seg)
    np.save(os.path.join(base, 'depth.npy'), depth)

    with open(os.path.join(base, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2, default=str)


def make_spectator_follow(spectator, vehicle, distance=8.0, height=3.0):
    vt = vehicle.get_transform()
    spectator.set_transform(
        carla.Transform(
            vt.location + vt.get_forward_vector() * -distance + carla.Location(z=height),
            carla.Rotation(pitch=-10, yaw=vt.rotation.yaw)
        )
    )


def create_route(world, start_location, num_waypoints=200, step=2.0):
    map = world.get_map()
    wp = map.get_waypoint(start_location)
    route = []
    for _ in range(num_waypoints):
        next_wps = wp.next(step)
        if not next_wps:
            break
        wp = next_wps[0]
        route.append(wp)
    return route


def get_vehicle_speed(vehicle):
    v = vehicle.get_velocity()
    return 3.6 * np.sqrt(v.x**2 + v.y**2 + v.z**2)
