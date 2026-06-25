import carla
import numpy as np
from config import CAMERA_POSITIONS, IMAGE_W, IMAGE_H, FOV


class SensorSuite:
    def __init__(self, world, vehicle):
        self.world = world
        self.vehicle = vehicle
        self.cameras = []
        self.data = {}

    def setup_all_cameras(self):
        bp_lib = self.world.get_blueprint_library()

        for name, loc, rot, fov in CAMERA_POSITIONS:
            rgb_bp = bp_lib.find('sensor.camera.rgb')
            rgb_bp.set_attribute('image_size_x', str(IMAGE_W))
            rgb_bp.set_attribute('image_size_y', str(IMAGE_H))
            rgb_bp.set_attribute('fov', str(fov or FOV))

            seg_bp = bp_lib.find('sensor.camera.semantic_segmentation')
            seg_bp.set_attribute('image_size_x', str(IMAGE_W))
            seg_bp.set_attribute('image_size_y', str(IMAGE_H))
            seg_bp.set_attribute('fov', str(fov or FOV))

            depth_bp = bp_lib.find('sensor.camera.depth')
            depth_bp.set_attribute('image_size_x', str(IMAGE_W))
            depth_bp.set_attribute('image_size_y', str(IMAGE_H))
            depth_bp.set_attribute('fov', str(fov or FOV))

            transform = carla.Transform(
                carla.Location(x=loc[0], y=loc[1], z=loc[2]),
                carla.Rotation(pitch=rot[0], yaw=rot[1], roll=rot[2])
            )

            rgb = self.world.spawn_actor(rgb_bp, transform, attach_to=self.vehicle)
            seg = self.world.spawn_actor(seg_bp, transform, attach_to=self.vehicle)
            depth = self.world.spawn_actor(depth_bp, transform, attach_to=self.vehicle)

            self.data[f'{name}_rgb'] = None
            self.data[f'{name}_seg'] = None
            self.data[f'{name}_depth'] = None

            rgb.listen(self._make_callback(f'{name}_rgb', 'rgb'))
            seg.listen(self._make_callback(f'{name}_seg', 'seg'))
            depth.listen(self._make_callback(f'{name}_depth', 'depth'))

            self.cameras.extend([
                (f'{name}_rgb', rgb),
                (f'{name}_seg', seg),
                (f'{name}_depth', depth),
            ])

        return self.cameras

    def _make_callback(self, name, cam_type):
        def cb(image):
            arr = np.frombuffer(image.raw_data, dtype=np.uint8)
            arr = arr.reshape((image.height, image.width, 4))

            if cam_type == 'depth':
                bgr = arr[:, :, :3].astype(np.float32)
                d = bgr[:, :, 0] + bgr[:, :, 1] * 256.0 + bgr[:, :, 2] * 256.0 * 256.0
                self.data[name] = d / (256.0 * 256.0 * 256.0 - 1) * 1000.0
            elif cam_type == 'seg':
                self.data[name] = arr[:, :, 2]
            else:
                self.data[name] = arr[:, :, :3][:, :, ::-1]
        return cb

    def destroy_all(self):
        for name, cam in self.cameras:
            cam.stop()
            cam.destroy()
        self.cameras.clear()
        self.data.clear()
