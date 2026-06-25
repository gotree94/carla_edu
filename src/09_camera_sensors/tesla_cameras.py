import carla
import time
import numpy as np
import cv2

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
bp_lib = world.get_blueprint_library()

vehicle_bp = bp_lib.find('vehicle.tesla.model3')
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(vehicle_bp, spawn_point)

camera_configs = [
    ("Front Center", carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=0), 90),
    ("Front Left",   carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=45), 90),
    ("Front Right",  carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=-45), 90),
    ("Left",         carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=90), 90),
    ("Right",        carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=-90), 90),
    ("Rear Center",  carla.Location(x=-1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=180), 90),
    ("Rear Left",    carla.Location(x=-1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=135), 90),
    ("Rear Right",   carla.Location(x=-1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=-135), 90),
]

cameras = []
image_data = {}

for name, loc, rot, fov in camera_configs:
    bp = bp_lib.find('sensor.camera.rgb')
    bp.set_attribute('image_size_x', '640')
    bp.set_attribute('image_size_y', '480')
    bp.set_attribute('fov', str(fov))
    bp.set_attribute('sensor_tick', '0.1')

    transform = carla.Transform(loc, rot)
    cam = world.spawn_actor(bp, transform, attach_to=vehicle)
    cameras.append((name, cam))
    image_data[name] = None

    def make_cb(n):
        def cb(image):
            arr = np.frombuffer(image.raw_data, dtype=np.uint8)
            arr = arr.reshape((image.height, image.width, 4))
            image_data[n] = arr[:, :, :3]
        return cb

    cam.listen(make_cb(name))
    print(f"Camera added: {name}")

spectator = world.get_spectator()

try:
    for i in range(300):
        control = carla.VehicleControl(throttle=0.3, steer=0.0)
        vehicle.apply_control(control)

        vt = vehicle.get_transform()
        spectator.set_transform(
            carla.Transform(
                vt.location + vt.get_forward_vector() * -8 + carla.Location(z=3),
                carla.Rotation(pitch=-10, yaw=vt.rotation.yaw)))

        if all(image_data.values()) and i % 5 == 0:
            top_row = np.hstack([
                image_data['Front Left'],
                image_data['Front Center'],
                image_data['Front Right']
            ])
            mid_row = np.hstack([
                image_data['Left'],
                np.zeros((480, 640, 3), dtype=np.uint8),
                image_data['Right']
            ])
            bot_row = np.hstack([
                image_data['Rear Left'],
                image_data['Rear Center'],
                image_data['Rear Right']
            ])
            display = np.vstack([top_row, mid_row, bot_row])
            display = cv2.resize(display, (960, 720))
            cv2.imshow('Tesla 8-Camera View', display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        time.sleep(0.05)

finally:
    for name, cam in cameras:
        cam.stop()
        cam.destroy()
    vehicle.destroy()
    cv2.destroyAllWindows()
