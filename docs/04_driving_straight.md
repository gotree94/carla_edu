# Step 04: Driving Straight

> 참고 영상: [Tutorial 4 Driving Straight with Carla Simulator](https://youtu.be/jIK9sanumuU)

## VehicleControl

CARLA에서 차량을 제어하려면 `carla.VehicleControl` 객체를 사용합니다.

```python
control = carla.VehicleControl()
control.throttle = 0.5    # 엑셀 (0.0 ~ 1.0)
control.steer = 0.0       # 조향 (-1.0 ~ 1.0)
control.brake = 0.0       # 브레이크 (0.0 ~ 1.0)
control.hand_brake = False
control.reverse = False
control.manual_gear_shift = False
control.gear = 0

vehicle.apply_control(control)
```

## 기본 직진 주행

```python
import carla
import time

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

# 차량 스폰
bp = world.get_blueprint_library().filter('model3')[0]
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(bp, spawn_point)

# Spectator 위치 설정
spectator = world.get_spectator()

try:
    for i in range(200):  # 약 200프레임 주행
        # 직진 주행
        control = carla.VehicleControl()
        control.throttle = 0.5
        control.steer = 0.0
        vehicle.apply_control(control)

        # Spectator를 차량 뒤에 위치
        vehicle_transform = vehicle.get_transform()
        spectator.set_transform(
            carla.Transform(
                vehicle_transform.location +
                vehicle_transform.get_forward_vector() * -8 +
                carla.Location(z=3),
                carla.Rotation(pitch=-10, yaw=vehicle_transform.rotation.yaw)
            ))

        # 상태 출력
        v = vehicle.get_velocity()
        speed = 3.6 * (v.x**2 + v.y**2 + v.z**2)**0.5
        print(f"Speed: {speed:.1f} km/h  "
              f"Loc: ({vehicle_transform.location.x:.1f}, "
              f"{vehicle_transform.location.y:.1f})")

        time.sleep(0.05)

finally:
    vehicle.destroy()
```

## 실행 결과

- 차량이 직진하며 속도가 증가
- 최고 속도에 도달하면 일정 속도 유지
- 맵 끝에 도달하면 장애물에 충돌

## 실습

1. throttle 값을 변경하며 속도 변화 관찰
2. steer 값을 조금씩 변경하여 곡선 주행
3. brake를 사용하여 정지해보기
