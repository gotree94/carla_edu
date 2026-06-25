# Step 06: Route Following

> 참고 영상: [Self-Driving with Carla Simulator: Final touches to route following](https://youtu.be/jIK9sanumuU)

## PID 제어 기반 경로 추종

정확한 경로 추종을 위해 PID(Proportional-Integral-Derivative) 제어기를 사용합니다.

### PID Controller

```python
class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0

    def control(self, error, dt=0.05):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative
```

### 완전한 경로 추종 코드

```python
import carla
import time
import math

class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0

    def control(self, error, dt=0.05):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative


client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
map = world.get_map()

# 차량 스폰
bp = world.get_blueprint_library().filter('model3')[0]
start_pose = map.get_spawn_points()[50]  # 직선 도로가 많은 위치
vehicle = world.spawn_actor(bp, start_pose)

# 전체 경로 생성
start_wp = map.get_waypoint(start_pose.location)
route = [start_wp]
for _ in range(100):
    next_wps = start_wp.next(2.0)
    if not next_wps:
        break
    start_wp = next_wps[0]
    route.append(start_wp)

print(f"경로: {len(route)}개 Waypoint")

# PID 제어기
steer_pid = PIDController(kp=0.8, ki=0.05, kd=0.1)
speed_pid = PIDController(kp=0.5, ki=0.1, kd=0.0)

target_speed = 30.0  # km/h
waypoint_index = 0
spectator = world.get_spectator()

try:
    while waypoint_index < len(route):
        target_wp = route[waypoint_index]
        vehicle_transform = vehicle.get_transform()
        vehicle_loc = vehicle_transform.location
        target_loc = target_wp.transform.location

        # 차량과 목표 Waypoint 사이의 거리
        dist = vehicle_loc.distance(target_loc)

        # 2m 이내 도달 시 다음 Waypoint
        if dist < 2.0:
            waypoint_index += 1
            if waypoint_index >= len(route):
                break
            target_wp = route[waypoint_index]
            target_loc = target_wp.transform.location

        # 조향각 계산 (PID)
        dx = target_loc.x - vehicle_loc.x
        dy = target_loc.y - vehicle_loc.y
        target_yaw = math.degrees(math.atan2(dy, dx))
        current_yaw = vehicle_transform.rotation.yaw
        error = (target_yaw - current_yaw + 180) % 360 - 180

        steer = steer_pid.control(error / 90.0)

        # 속도 제어 (PID)
        v = vehicle.get_velocity()
        current_speed = 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)
        speed_error = target_speed - current_speed
        throttle = speed_pid.control(speed_error)

        # 제어 적용
        control = carla.VehicleControl()
        control.steer = max(-1.0, min(1.0, steer))
        control.throttle = max(0.0, min(1.0, throttle))
        vehicle.apply_control(control)

        # Spectator
        spectator.set_transform(
            carla.Transform(
                vehicle_loc + vehicle_transform.get_forward_vector() * -10 +
                carla.Location(z=4),
                carla.Rotation(pitch=-15, yaw=vehicle_transform.rotation.yaw)))

        time.sleep(0.05)

finally:
    # 정지
    control = carla.VehicleControl()
    control.throttle = 0.0
    control.brake = 1.0
    vehicle.apply_control(control)
    time.sleep(0.5)
    vehicle.destroy()
```

## PID 튜닝 가이드

| 파라미터 | 역할 | 값이 클 때 | 값이 작을 때 |
|----------|------|-----------|------------|
| Kp (Proportional) | 현재 오차에 비례 | 진동, 과도한 반응 | 느린 반응 |
| Ki (Integral) | 누적 오차 보정 | 오버슈트 | 정상 상태 오차 |
| Kd (Derivative) | 변화율 예측 | 노이즈 증폭 | 진동 억제 부족 |
