# Step 09: Camera Sensors

> Tesla-style 카메라, Semantic Segmentation, Depth 센서

## CARLA 센서 종류

| 센서 | 용도 |
|------|------|
| `sensor.camera.rgb` | 일반 RGB 카메라 |
| `sensor.camera.semantic_segmentation` | 의미론적 분할 (픽셀 단위 클래스) |
| `sensor.camera.depth` | 깊이 맵 (픽셀 단위 거리) |
| `sensor.camera.instance_segmentation` | 인스턴스 분할 |
| `sensor.lidar.ray_cast` | LiDAR 포인트 클라우드 |
| `sensor.other.gnss` | GPS 좌표 |
| `sensor.other.imu` | IMU (가속도, 자이로) |

## 3종 카메라 동시 사용

```python
import carla
import time
import numpy as np
import cv2

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
bp_lib = world.get_blueprint_library()

# 차량 스폰
vehicle_bp = bp_lib.find('vehicle.tesla.model3')
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(vehicle_bp, spawn_point)

# 카메라 설정
camera_transform = carla.Transform(
    carla.Location(x=1.5, z=2.4),
    carla.Rotation(pitch=0)
)

# 1. RGB 카메라
rgb_bp = bp_lib.find('sensor.camera.rgb')
rgb_bp.set_attribute('image_size_x', '800')
rgb_bp.set_attribute('image_size_y', '600')
rgb_bp.set_attribute('fov', '90')
rgb_camera = world.spawn_actor(rgb_bp, camera_transform, attach_to=vehicle)

# 2. Semantic Segmentation 카메라
seg_bp = bp_lib.find('sensor.camera.semantic_segmentation')
seg_bp.set_attribute('image_size_x', '800')
seg_bp.set_attribute('image_size_y', '600')
seg_bp.set_attribute('fov', '90')
seg_camera = world.spawn_actor(seg_bp, camera_transform, attach_to=vehicle)

# 3. Depth 카메라
depth_bp = bp_lib.find('sensor.camera.depth')
depth_bp.set_attribute('image_size_x', '800')
depth_bp.set_attribute('image_size_y', '600')
depth_bp.set_attribute('fov', '90')
depth_camera = world.spawn_actor(depth_bp, camera_transform, attach_to=vehicle)

# 데이터 저장용
rgb_data = [None]
seg_data = [None]
depth_data = [None]

def process_rgb(image):
    arr = np.frombuffer(image.raw_data, dtype=np.uint8)
    arr = arr.reshape((image.height, image.width, 4))
    rgb_data[0] = arr[:, :, :3][:, :, ::-1]  # BGRA -> RGB

def process_seg(image):
    arr = np.frombuffer(image.raw_data, dtype=np.uint8)
    arr = arr.reshape((image.height, image.width, 4))
    # Semantic segmentation은 R 채널에 클래스 ID 저장
    seg_data[0] = arr[:, :, 2]  # 클래스 ID 맵

def process_depth(image):
    arr = np.frombuffer(image.raw_data, dtype=np.uint8)
    arr = arr.reshape((image.height, image.width, 4))
    # Depth 데이터 복원
    bgr = arr[:, :, :3].astype(np.float32)
    normalized = bgr[:, :, 0] + bgr[:, :, 1] * 256.0 + bgr[:, :, 2] * 256.0 * 256.0
    normalized = normalized / (256.0 * 256.0 * 256.0 - 1)
    depth_data[0] = normalized * 1000.0  # 밀리미터 단위

rgb_camera.listen(process_rgb)
seg_camera.listen(process_seg)
depth_camera.listen(process_depth)

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

        if rgb_data[0] is not None and seg_data[0] is not None and depth_data[0] is not None:
            # Segmentation 컬러맵 적용
            seg_colormap = apply_segmentation_colormap(seg_data[0])

            # Depth 시각화 (Normalize)
            depth_vis = (depth_data[0] / depth_data[0].max() * 255).astype(np.uint8)
            depth_vis = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)

            # 화면 표시
            stacked = np.hstack([rgb_data[0], seg_colormap, depth_vis])
            cv2.imshow('CARLA Sensors (RGB | Seg | Depth)', stacked)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        time.sleep(0.05)

finally:
    rgb_camera.stop()
    seg_camera.stop()
    depth_camera.stop()
    rgb_camera.destroy()
    seg_camera.destroy()
    depth_camera.destroy()
    vehicle.destroy()
    cv2.destroyAllWindows()


def apply_segmentation_colormap(seg_array):
    """CARLA Segmentation 클래스를 컬러맵으로 변환"""
    # CARLA 시맨틱 분할 클래스
    classes = {
        0: (0, 0, 0),        # None
        1: (70, 70, 70),     # Buildings
        2: (100, 40, 40),    # Fences
        3: (55, 90, 80),     # Other
        4: (220, 20, 60),    # Pedestrians
        5: (153, 153, 153),  # Poles
        6: (157, 234, 50),   # RoadLines
        7: (128, 64, 128),   # Roads
        8: (244, 35, 232),   # Sidewalks
        9: (107, 142, 35),   # Vegetation
        10: (0, 0, 142),     # Vehicles
        11: (102, 102, 156), # Walls
        12: (220, 220, 0),   # Traffic Signs
        13: (70, 130, 180),  # Sky
        14: (81, 0, 81),     # Ground
        15: (150, 100, 100), # Bridges
        16: (230, 150, 140), # RailTracks
        17: (180, 165, 180), # GuardRails
        18: (250, 170, 30),  # TrafficLights
        19: (110, 190, 160), # Static
        20: (170, 120, 50),  # Dynamnic
        21: (45, 60, 150),   # Water
        22: (145, 170, 100), # Terrain
    }
    h, w = seg_array.shape
    color_img = np.zeros((h, w, 3), dtype=np.uint8)
    for class_id, color in classes.items():
        mask = seg_array == class_id
        color_img[mask] = color
    return color_img
```

## Tesla-style 카메라 구성

Tesla는 8개의 카메라를 사용합니다. 이를 시뮬레이션:

```python
camera_configs = [
    # (위치, 회전, FOV, 이름)
    (carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=0), 90, "Front"),
    (carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=45), 90, "Front-Left"),
    (carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=-45), 90, "Front-Right"),
    (carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=90), 90, "Left"),
    (carla.Location(x=1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=-90), 90, "Right"),
    (carla.Location(x=-1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=180), 90, "Rear"),
    (carla.Location(x=-1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=135), 90, "Rear-Left"),
    (carla.Location(x=-1.5, y=0, z=2.4), carla.Rotation(pitch=0, yaw=-135), 90, "Rear-Right"),
]
```
