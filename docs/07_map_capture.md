# Step 07: Map Capture

> 참고 영상: [Carla Sim: How to capture the Map as you drive](https://youtu.be/jIK9sanumuU)

## 주행 중 맵 데이터 캡처

차량이 주행하면서 주변 환경 데이터를 수집하고 저장하는 방법을 알아봅니다.

### RGB 카메라 센서 부착

```python
import carla
import time
import numpy as np
import cv2

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

# 차량 스폰
bp = world.get_blueprint_library().filter('model3')[0]
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(bp, spawn_point)

# RGB 카메라 블루프린트
camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '800')
camera_bp.set_attribute('image_size_y', '600')
camera_bp.set_attribute('fov', '90')

# 카메라 Transform (차량 전면)
camera_transform = carla.Transform(
    carla.Location(x=1.5, z=2.4),
    carla.Rotation(pitch=0)
)

# 카메라 스폰 및 차량에 부착
camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

# 이미지 저장을 위한 리스트
frame_count = 0
captured_images = []

# 콜백 함수: 카메라 데이터 수신 시 호출
def process_image(image):
    global frame_count, captured_images
    # raw 데이터를 numpy 배열로 변환
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = array.reshape((image.height, image.width, 4))  # BGRA
    array = array[:, :, :3]  # BGR
    array = array[:, :, ::-1]  # BGR -> RGB

    captured_images.append({
        'frame': frame_count,
        'data': array,
        'transform': image.transform,
        'timestamp': image.timestamp
    })
    frame_count += 1

# 콜백 등록
camera.listen(process_image)

# 차량 주행
spectator = world.get_spectator()
try:
    for i in range(100):
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
    camera.destroy()
    vehicle.destroy()

# 캡처된 이미지 저장
for i, cap in enumerate(captured_images[::5]):  # 5프레임마다 저장
    cv2.imwrite(f'capture_{i:04d}.png',
                cv2.cvtColor(cap['data'], cv2.COLOR_RGB2BGR))

print(f"총 {len(captured_images)}프레임 캡처, {len(captured_images)//5}장 저장")
```

### 데이터 수집 시 고려사항

1. **동기화**: `world.tick()`과 센서 데이터 타이밍 일치
2. **저장 형식**: PNG(무손실) 또는 JPEG(압축)
3. **메타데이터**: 위치, 시간, 속도 정보 함께 저장
4. **다양성**: 여러 날씨, 시간대, 위치에서 수집
