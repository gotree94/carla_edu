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

class SensorManager:
    def __init__(self, world, vehicle):
        self.world = world
        self.vehicle = vehicle
        self.sensors = []
        self.data = {}

    def add_camera(self, bp_name, transform, attr=None, name=None):
        bp = self.world.get_blueprint_library().find(bp_name)
        if attr:
            for k, v in attr.items():
                bp.set_attribute(k, v)
        sensor = self.world.spawn_actor(bp, transform, attach_to=self.vehicle)
        name = name or bp_name
        self.data[name] = None
        self.sensors.append((name, sensor))

        def make_callback(n):
            def cb(image):
                arr = np.frombuffer(image.raw_data, dtype=np.uint8)
                arr = arr.reshape((image.height, image.width, 4))

                if 'depth' in n:
                    bgr = arr[:, :, :3].astype(np.float32)
                    d = bgr[:, :, 0] + bgr[:, :, 1] * 256.0 + bgr[:, :, 2] * 256.0 * 256.0
                    d = d / (256.0 * 256.0 * 256.0 - 1) * 1000.0
                    self.data[n] = d
                elif 'segmentation' in n:
                    self.data[n] = arr[:, :, 2]
                else:
                    self.data[n] = arr[:, :, :3][:, :, ::-1]
            return cb

        sensor.listen(make_callback(name))
        return sensor

    def destroy(self):
        for _, s in self.sensors:
            s.stop()
            s.destroy()


camera_transform = carla.Transform(
    carla.Location(x=1.5, z=2.4),
    carla.Rotation(pitch=0)
)

cam_attrs = {
    'image_size_x': '800',
    'image_size_y': '600',
    'fov': '90',
    'sensor_tick': '0.05'
}

sm = SensorManager(world, vehicle)
sm.add_camera('sensor.camera.rgb', camera_transform, cam_attrs, 'rgb')
sm.add_camera('sensor.camera.semantic_segmentation', camera_transform, cam_attrs, 'seg')
sm.add_camera('sensor.camera.depth', camera_transform, cam_attrs, 'depth')

SEG_COLORS = {
    0: (0, 0, 0), 1: (70, 70, 70), 2: (100, 40, 40),
    3: (55, 90, 80), 4: (220, 20, 60), 5: (153, 153, 153),
    6: (157, 234, 50), 7: (128, 64, 128), 8: (244, 35, 232),
    9: (107, 142, 35), 10: (0, 0, 142), 11: (102, 102, 156),
    12: (220, 220, 0), 13: (70, 130, 180),
}

def colorize_seg(seg):
    h, w = seg.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)
    for cid, color in SEG_COLORS.items():
        out[seg == cid] = color
    return out

spectator = world.get_spectator()

try:
    for i in range(400):
        control = carla.VehicleControl(throttle=0.4, steer=0.0)
        vehicle.apply_control(control)

        vt = vehicle.get_transform()
        spectator.set_transform(
            carla.Transform(
                vt.location + vt.get_forward_vector() * -8 + carla.Location(z=3),
                carla.Rotation(pitch=-10, yaw=vt.rotation.yaw)))

        if all(sm.data.values()):
            rgb = sm.data['rgb']
            seg = colorize_seg(sm.data['seg'])
            depth = sm.data['depth']
            depth_norm = (depth / np.max(depth) * 255).astype(np.uint8)
            depth_vis = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)

            display = np.vstack([
                np.hstack([rgb, seg]),
                np.hstack([depth_vis, np.zeros_like(rgb)])
            ])

            cv2.imshow('CARLA Sensors', display)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        time.sleep(0.05)

finally:
    sm.destroy()
    vehicle.destroy()
    cv2.destroyAllWindows()
