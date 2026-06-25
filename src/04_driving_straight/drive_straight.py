import carla
import time
import math

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
bp_lib = world.get_blueprint_library()

vehicle_bp = bp_lib.filter('model3')[0]
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(vehicle_bp, spawn_point)
print(f"Spawned at: {spawn_point.location}")

spectator = world.get_spectator()

try:
    for i in range(300):
        control = carla.VehicleControl()
        control.throttle = 0.5
        control.steer = 0.0
        control.brake = 0.0
        vehicle.apply_control(control)

        vt = vehicle.get_transform()
        spectator.set_transform(
            carla.Transform(
                vt.location + vt.get_forward_vector() * -8 + carla.Location(z=3),
                carla.Rotation(pitch=-10, yaw=vt.rotation.yaw)))

        v = vehicle.get_velocity()
        speed = 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)

        if i % 20 == 0:
            print(f"Frame: {i:3d} | Speed: {speed:.1f} km/h | "
                  f"Loc: ({vt.location.x:.1f}, {vt.location.y:.1f})")

        time.sleep(0.05)

finally:
    control = carla.VehicleControl()
    control.brake = 1.0
    vehicle.apply_control(control)
    time.sleep(1)
    vehicle.destroy()
    print("Stopped and cleaned up")
