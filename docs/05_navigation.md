# Step 05: Navigation Basics

> 참고 영상: [Self-Driving Basics: Navigation - The Fun Part](https://youtu.be/jIK9sanumuU)

## Waypoint 기반 내비게이션

CARLA의 `carla.Map` 객체는 Waypoint 기반 길 찾기를 제공합니다.

### Waypoint 구조

```
Waypoint
├── transform (carla.Transform) - 위치/회전
├── lane_id - 차선 ID
├── road_id - 도로 ID
├── lane_type - 차선 유형 (Driving, Sidewalk, 등)
├── lane_width - 차선 폭
├── is_junction - 교차로 여부
├── next_until_lane_end(count) - 다음 Waypoint 목록
└── get_junction() - 교차로 정보
```

### 경로 생성 예시

```python
import carla
import time

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
map = world.get_map()

# 차량 스폰
bp = world.get_blueprint_library().filter('model3')[0]
start_pose = map.get_spawn_points()[0]
vehicle = world.spawn_actor(bp, start_pose)

# 시작 지점의 Waypoint 획득
waypoint = map.get_waypoint(start_pose.location)

# 경로 생성: 20개의 Waypoint 수집
route = []
for _ in range(20):
    next_wps = waypoint.next(2.0)  # 2m 앞 Waypoint
    if not next_wps:
        break
    waypoint = next_wps[0]
    route.append(waypoint)

print(f"경로 생성 완료: {len(route)}개 Waypoint")

# 경로 따라 주행
spectator = world.get_spectator()

for wp in route:
    # 다음 Waypoint 방향으로 조향
    vehicle_loc = vehicle.get_location()
    wp_loc = wp.transform.location

    # 방향 벡터 계산
    dx = wp_loc.x - vehicle_loc.x
    dy = wp_loc.y - vehicle_loc.y
    import math
    target_yaw = math.degrees(math.atan2(dy, dx))
    current_yaw = vehicle.get_transform().rotation.yaw

    # 조향각 계산
    steer = (target_yaw - current_yaw) / 90.0
    steer = max(-1.0, min(1.0, steer))

    control = carla.VehicleControl()
    control.throttle = 0.4
    control.steer = steer
    vehicle.apply_control(control)

    # Spectator 업데이트
    vt = vehicle.get_transform()
    spectator.set_transform(
        carla.Transform(
            vt.location + vt.get_forward_vector() * -8 + carla.Location(z=3),
            carla.Rotation(pitch=-10, yaw=vt.rotation.yaw)))

    time.sleep(0.1)
```

## 핵심 함수

### Waypoint.next(distance)
- 현재 Waypoint에서 distance만큼 앞에 있는 Waypoint 목록 반환
- 여러 차선이 있을 경우 여러 개 반환 가능
- 일반적으로 `next_waypoints[0]` 사용

### Map.get_waypoint(location)
- 특정 위치에서 가장 가까운 도로 위의 Waypoint 반환
- `project_to_road=True`로 도로에 투영

### Waypoint.previous(distance)
- 뒤쪽 방향 Waypoint 반환
