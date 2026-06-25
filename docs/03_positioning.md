# Step 03: Positioning on the Map

> 참고 영상: [Self-driving with Carla Sim: Positioning on the map](https://youtu.be/jIK9sanumuU)

## 핵심 개념

### Transform (위치 + 회전)
- `carla.Location(x, y, z)` - 3D 공간 좌표
- `carla.Rotation(pitch, yaw, roll)` - 회전 각도
- `carla.Transform(location, rotation)` - 위치 + 회전

### Waypoint (경유지)
- 도로 위의 특정 지점
- 차선 정보, 도로 폭, 다음 Waypoint 등을 포함
- `carla.Map.get_waypoint(location)`으로 획득

### Spawn Points (스폰 포인트)
- 맵에 미리 정의된 차량 생성 위치
- `world.get_map().get_spawn_points()`로 획득

## 주요 코드

```python
import carla

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
map = world.get_map()

# 1. 스폰 포인트 리스트 확인
spawn_points = map.get_spawn_points()
print(f"총 {len(spawn_points)}개의 스폰 포인트")
for i, sp in enumerate(spawn_points[:5]):
    print(f"  {i}: {sp.location}")

# 2. 특정 위치의 Waypoint 획득
location = carla.Location(x=30, y=-20, z=0)
waypoint = map.get_waypoint(location, project_to_road=True)
print(f"가장 가까운 도로 Waypoint: {waypoint.transform.location}")

# 3. 차량을 특정 위치에 스폰
bp = world.get_blueprint_library().filter('model3')[0]
vehicle = world.spawn_actor(bp, spawn_points[5])

# 4. Spectator 위치 설정
spectator = world.get_spectator()
spectator.set_transform(
    carla.Transform(
        vehicle.get_transform().location + carla.Location(z=50),
        carla.Rotation(pitch=-90)
    ))

# 5. 차량 Transform 정보 읽기
t = vehicle.get_transform()
print(f"위치: x={t.location.x:.2f}, y={t.location.y:.2f}, z={t.location.z:.2f}")
print(f"회전: pitch={t.rotation.pitch:.2f}, yaw={t.rotation.yaw:.2f}, roll={t.rotation.roll:.2f}")

# 6. 차량 Velocity 정보
v = vehicle.get_velocity()
speed = 3.6 * (v.x**2 + v.y**2 + v.z**2)**0.5  # km/h
print(f"속도: {speed:.2f} km/h")
```

## 실습

1. 차량을 여러 스폰 포인트에 스폰해보기
2. 스폰 포인트 좌표를 맵에 시각화하기
3. Waypoint를 따라 이동하며 위치 정보 출력하기
