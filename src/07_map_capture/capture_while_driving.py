import carla
import time
import math
import numpy as np
import cv2
import os

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
bp_lib = world.get_blueprint_library()

vehicle_bp = bp_lib.filter('model3')[0]
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(vehicle_bp, spawn_point)

camera_bp = bp_lib.find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '1280')
camera_bp.set_attribute('image_size_y', '720')
camera_bp.set_attribute('fov', '100')
camera_bp.set_attribute('sensor_tick', '0.1')

camera_transform = carla.Transform(
    carla.Location(x=1.5, z=2.4),
    carla.Rotation(pitch=0)
)
camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

os.makedirs('captures', exist_ok=True)
frame = [0]
captured = []

def on_image(image):
    arr = np.frombuffer(image.raw_data, dtype=np.uint8)
    arr = arr.reshape((image.height, image.width, 4))
    bgr = arr[:, :, :3]
    captured.append({
        'frame': frame[0],
        'data': bgr.copy(),
        'timestamp': image.timestamp
    })
    frame[0] += 1

camera.listen(on_image)

spectator = world.get_spectator()

try:
    for i in range(200):
        control = carla.VehicleControl(throttle=0.4, steer=0.0)
        vehicle.apply_control(control)

        vt = vehicle.get_transform()
        spectator.set_transform(
            carla.Transform(
                vt.location + vt.get_forward_vector() * -8 + carla.Location(z=3),
                carla.Rotation(pitch=-10, yaw=vt.rotation.yaw)))
        time.sleep(0.05)

finally:
    camera.stop()

    for i, cap in enumerate(captured[::5]):
        fname = f'captures/frame_{i:04d}.png'
        cv2.imwrite(fname, cap['data'])

    print(f"Captured {len(captured)} frames, saved {len(captured)//5} images")

    camera.destroy()
    vehicle.destroy()
