# Step 08: Follow a Car

> 참고 영상: [How to follow a car in Carla Simulator](https://youtu.be/jIK9sanumuU)

## 앞차 추종 (Adaptive Cruise Control)

앞차와의 거리를 일정하게 유지하며 주행하는 ACC(Adaptive Cruise Control)를 구현합니다.

### 기본 구조

```python
import carla
import time
import math
import numpy as np

class ACCController:
    def __init__(self, target_distance=10.0, speed_limit=40.0):
        self.target_distance = target_distance  # 목표 추종 거리 (m)
        self.speed_limit = speed_limit          # 최대 속도 (km/h)
        self.kp_dist = 0.5                      # 거리 P 게인
        self.kp_speed = 0.3                     # 속도 P 게인

    def control(self, ego_vehicle, lead_vehicle, dt=0.05):
        # 앞차와의 거리 계산
        ego_loc = ego_vehicle.get_location()
        lead_loc = lead_vehicle.get_location()
        distance = ego_loc.distance(lead_loc)

        # 상대 속도 계산
        ego_vel = ego_vehicle.get_velocity()
        lead_vel = lead_vehicle.get_velocity()
        ego_speed = 3.6 * math.sqrt(ego_vel.x**2 + ego_vel.y**2 + ego_vel.z**2)
        lead_speed = 3.6 * math.sqrt(lead_vel.x**2 + lead_vel.y**2 + lead_vel.z**2)

        # 거리 오차
        distance_error = distance - self.target_distance

        # 속도 제어
        if distance < self.target_distance * 0.7:  # 너무 가까우면 브레이크
            throttle = 0.0
            brake = min(1.0, (self.target_distance - distance) / self.target_distance)
        elif distance > self.target_distance * 1.3:  # 너무 멀면 가속
            throttle = min(1.0, distance_error * self.kp_dist)
            brake = 0.0
        else:
            # 추종 모드: 앞차 속도에 맞춤
            speed_error = lead_speed - ego_speed
            if speed_error > 0:
                throttle = min(1.0, speed_error * self.kp_speed)
                brake = 0.0
            else:
                throttle = 0.0
                brake = min(1.0, -speed_error * self.kp_speed)

        # 조향 (앞차 방향으로)
        dx = lead_loc.x - ego_loc.x
        dy = lead_loc.y - ego_loc.y
        target_yaw = math.degrees(math.atan2(dy, dx))
        current_yaw = ego_vehicle.get_transform().rotation.yaw
        steer_error = (target_yaw - current_yaw + 180) % 360 - 180
        steer = max(-1.0, min(1.0, steer_error / 90.0))

        control = carla.VehicleControl()
        control.throttle = throttle
        control.brake = brake
        control.steer = steer
        return control, distance, ego_speed, lead_speed
```

### 전체 실행 코드

```python
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
bp_lib = world.get_blueprint_library()

# Ego 차량 스폰
ego_bp = bp_lib.filter('model3')[0]
ego_spawn = world.get_map().get_spawn_points()[50]
ego_vehicle = world.spawn_actor(ego_bp, ego_spawn)

# Lead 차량 (앞차) 스폰 - Ego 차량 앞에 위치
lead_bp = bp_lib.filter('audi')[0]
lead_transform = carla.Transform(
    ego_spawn.location + carla.Location(x=15.0),
    ego_spawn.rotation
)
lead_vehicle = world.spawn_actor(lead_bp, lead_transform)

# Lead 차량 Autopilot 활성화
lead_vehicle.set_autopilot(True)

acc = ACCController(target_distance=10.0, speed_limit=40.0)
spectator = world.get_spectator()

try:
    for i in range(500):
        control, dist, ego_speed, lead_speed = acc.control(
            ego_vehicle, lead_vehicle)
        ego_vehicle.apply_control(control)

        # Spectator 위치 업데이트
        vt = ego_vehicle.get_transform()
        spectator.set_transform(
            carla.Transform(
                vt.location + vt.get_forward_vector() * -12 + carla.Location(z=5),
                carla.Rotation(pitch=-20, yaw=vt.rotation.yaw)))

        if i % 10 == 0:
            print(f"거리: {dist:.1f}m | Ego: {ego_speed:.0f} km/h | "
                  f"Lead: {lead_speed:.0f} km/h | "
                  f"Throttle: {control.throttle:.2f} | Brake: {control.brake:.2f}")

        time.sleep(0.05)

finally:
    ego_vehicle.destroy()
    lead_vehicle.destroy()
```

## ACC 알고리즘 동작

```
                     목표 거리 (10m)
                     ←-----------→
┌─────────┐                        ┌─────────┐
│  Ego    │ ═══════════════════════ │  Lead   │
│  Vehicle│      추종 거리          │  Vehicle│
└─────────┘                        └─────────┘
   속도 조절                         Autopilot
   거리 유지                         주행 중
```

| 상황 | 동작 |
|------|------|
| 거리 < 7m | 브레이크 작동 |
| 7m ≤ 거리 ≤ 13m | 앞차 속도에 맞춰 추종 |
| 거리 > 13m | 가속하여 거리 회복 |
| 앞차 정지 | 정지 후 거리 유지 |
