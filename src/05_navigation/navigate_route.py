import carla
import time
import math

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
map = world.get_map()
bp_lib = world.get_blueprint_library()

vehicle_bp = bp_lib.filter('model3')[0]
spawn_point = map.get_spawn_points()[0]
vehicle = world.spawn_actor(vehicle_bp, spawn_point)

start_wp = map.get_waypoint(spawn_point.location)
route = []
current_wp = start_wp
for _ in range(50):
    next_wps = current_wp.next(3.0)
    if not next_wps:
        break
    current_wp = next_wps[0]
    route.append(current_wp)

print(f"Route created with {len(route)} waypoints")

spectator = world.get_spectator()
target_index = 0

try:
    while target_index < len(route):
        target = route[target_index]
        vt = vehicle.get_transform()
        vl = vt.location
        tl = target.transform.location

        dist = vl.distance(tl)
        if dist < 2.0:
            target_index += 1
            continue

        dx = tl.x - vl.x
        dy = tl.y - vl.y
        target_yaw = math.degrees(math.atan2(dy, dx))
        current_yaw = vt.rotation.yaw
        diff = (target_yaw - current_yaw + 180) % 360 - 180
        steer = max(-1.0, min(1.0, diff / 90.0))

        control = carla.VehicleControl()
        control.throttle = 0.5
        control.steer = steer
        vehicle.apply_control(control)

        spectator.set_transform(
            carla.Transform(
                vl + vt.get_forward_vector() * -8 + carla.Location(z=3),
                carla.Rotation(pitch=-10, yaw=vt.rotation.yaw)))

        v = vehicle.get_velocity()
        speed = 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)

        if target_index % 5 == 0:
            print(f"WP [{target_index}/{len(route)}] | "
                  f"Dist: {dist:.1f}m | Speed: {speed:.1f} km/h | "
                  f"Steer: {steer:.2f}")

        time.sleep(0.05)

    print("Route complete!")
    control = carla.VehicleControl(brake=1.0)
    vehicle.apply_control(control)
    time.sleep(1)

finally:
    vehicle.destroy()
