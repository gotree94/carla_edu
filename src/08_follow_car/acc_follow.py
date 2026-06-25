import carla
import time
import math


class ACC:
    def __init__(self, target_dist=8.0, max_speed=40.0):
        self.target_dist = target_dist
        self.max_speed = max_speed

    def compute_control(self, ego, lead):
        ego_loc = ego.get_location()
        lead_loc = lead.get_location()
        dist = ego_loc.distance(lead_loc)

        ego_v = ego.get_velocity()
        lead_v = lead.get_velocity()
        ego_speed = 3.6 * math.sqrt(ego_v.x**2 + ego_v.y**2 + ego_v.z**2)
        lead_speed = 3.6 * math.sqrt(lead_v.x**2 + lead_v.y**2 + lead_v.z**2)

        if dist < self.target_dist * 0.6:
            brake = min(1.0, (self.target_dist - dist) / self.target_dist)
            throttle = 0.0
        elif dist > self.target_dist * 1.4:
            brake = 0.0
            throttle = min(1.0, (dist - self.target_dist) * 0.08)
        else:
            speed_diff = lead_speed - ego_speed
            if speed_diff > 0:
                throttle = min(1.0, speed_diff * 0.02)
                brake = 0.0
            else:
                throttle = 0.0
                brake = min(0.5, -speed_diff * 0.01)

        dx = lead_loc.x - ego_loc.x
        dy = lead_loc.y - ego_loc.y
        target_yaw = math.degrees(math.atan2(dy, dx))
        current_yaw = ego.get_transform().rotation.yaw
        err = (target_yaw - current_yaw + 180) % 360 - 180
        steer = max(-0.6, min(0.6, err / 90.0))

        return throttle, brake, steer, dist, ego_speed, lead_speed


client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
bp_lib = world.get_blueprint_library()

ego_bp = bp_lib.filter('model3')[0]
lead_bp = bp_lib.filter('audi')[0]

sp = world.get_map().get_spawn_points()[50]

ego = world.spawn_actor(ego_bp, sp)

lead_transform = carla.Transform(
    sp.location + carla.Location(x=12.0),
    sp.rotation
)
lead = world.spawn_actor(lead_bp, lead_transform)
lead.set_autopilot(True)

acc = ACC(target_dist=8.0, max_speed=40.0)
spectator = world.get_spectator()

try:
    for i in range(500):
        thr, brk, str_, dist, e_spd, l_spd = acc.compute_control(ego, lead)

        control = carla.VehicleControl(
            throttle=thr, brake=brk, steer=str_)
        ego.apply_control(control)

        vt = ego.get_transform()
        spectator.set_transform(
            carla.Transform(
                vt.location + vt.get_forward_vector() * -10 + carla.Location(z=4),
                carla.Rotation(pitch=-15, yaw=vt.rotation.yaw)))

        if i % 10 == 0:
            print(f"Dist:{dist:5.1f}m "
                  f"Ego:{e_spd:5.0f}km/h Lead:{l_spd:5.0f}km/h "
                  f"Thr:{thr:.2f} Brk:{brk:.2f} Str:{str_:.2f}")

        time.sleep(0.05)

finally:
    ego.destroy()
    lead.destroy()
