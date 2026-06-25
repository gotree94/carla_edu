import carla
import time
import math


class PID:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self._integral = 0.0
        self._prev_error = 0.0

    def control(self, error, dt=0.05):
        self._integral += error * dt
        derivative = (error - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = error
        return self.kp * error + self.ki * self._integral + self.kd * derivative

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0


client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
map = world.get_map()
bp_lib = world.get_blueprint_library()

vehicle_bp = bp_lib.filter('model3')[0]
spawn_point = map.get_spawn_points()[50]
vehicle = world.spawn_actor(vehicle_bp, spawn_point)

start_wp = map.get_waypoint(spawn_point.location)
route = []
wp = start_wp
for _ in range(200):
    next_wps = wp.next(2.0)
    if not next_wps:
        break
    wp = next_wps[0]
    route.append(wp)

print(f"Route: {len(route)} waypoints")

steer_pid = PID(kp=0.8, ki=0.05, kd=0.1)
speed_pid = PID(kp=0.5, ki=0.1, kd=0.0)
target_speed = 35.0

spectator = world.get_spectator()
wp_idx = 0

try:
    while wp_idx < len(route):
        target = route[wp_idx]
        vt = vehicle.get_transform()
        vl = vt.location
        tl = target.transform.location

        dist = vl.distance(tl)
        if dist < 2.0:
            wp_idx += 1
            if wp_idx >= len(route):
                break
            target = route[wp_idx]
            tl = target.transform.location

        dx = tl.x - vl.x
        dy = tl.y - vl.y
        target_yaw = math.degrees(math.atan2(dy, dx))
        current_yaw = vt.rotation.yaw
        error = (target_yaw - current_yaw + 180) % 360 - 180
        steer = steer_pid.control(error / 90.0)

        v = vehicle.get_velocity()
        current_speed = 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)
        speed_error = target_speed - current_speed
        throttle = speed_pid.control(speed_error)

        control = carla.VehicleControl()
        control.steer = max(-1.0, min(1.0, steer))
        control.throttle = max(0.0, min(1.0, throttle))
        vehicle.apply_control(control)

        spectator.set_transform(
            carla.Transform(
                vl + vt.get_forward_vector() * -10 + carla.Location(z=4),
                carla.Rotation(pitch=-15, yaw=vt.rotation.yaw)))

        if wp_idx % 20 == 0:
            print(f"WP[{wp_idx:3d}/{len(route)}] "
                  f"Dist:{dist:.1f}m Speed:{current_speed:.0f}km/h "
                  f"Steer:{steer:.2f} Throttle:{throttle:.2f}")

        time.sleep(0.05)

    print("Route completed!")

finally:
    control = carla.VehicleControl(brake=1.0)
    vehicle.apply_control(control)
    time.sleep(0.5)
    vehicle.destroy()
