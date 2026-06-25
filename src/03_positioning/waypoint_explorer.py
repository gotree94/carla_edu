import carla
import time

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
map = world.get_map()

spawn_point = map.get_spawn_points()[0]

waypoint = map.get_waypoint(spawn_point.location, project_to_road=True)
print(f"Initial waypoint:")
print(f"  Location: {waypoint.transform.location}")
print(f"  Road ID: {waypoint.road_id}")
print(f"  Lane ID: {waypoint.lane_id}")
print(f"  Lane Type: {waypoint.lane_type}")
print(f"  Lane Width: {waypoint.lane_width:.2f}m")
print(f"  Is Junction: {waypoint.is_junction}")

print("\nExploring 10 waypoints ahead...")
current_wp = waypoint
for i in range(10):
    next_wps = current_wp.next(5.0)
    if not next_wps:
        print(f"  [{i}] No more waypoints ahead")
        break
    current_wp = next_wps[0]
    print(f"  [{i}] Loc: ({current_wp.transform.location.x:.1f}, "
          f"{current_wp.transform.location.y:.1f}) "
          f"| Road: {current_wp.road_id} Lane: {current_wp.lane_id}")

print(f"\nRight lane change:")
right_wp = waypoint.get_right_lane()
if right_wp:
    print(f"  Right lane exists: Road={right_wp.road_id}, Lane={right_wp.lane_id}")

print(f"Left lane change:")
left_wp = waypoint.get_left_lane()
if left_wp:
    print(f"  Left lane exists: Road={left_wp.road_id}, Lane={left_wp.lane_id}")
