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

spectator = world.get_spectator()

try:
    for i in range(400):
        # Sine wave throttle for speed variation
        throttle = 0.3 + 0.3 * math.sin(i * 0.05)
        steer = 0.1 * math.sin(i * 0.03)

        control = carla.VehicleControl()
        control.throttle = max(0.0, min(1.0, throttle))
        control.steer = max(-1.0, min(1.0, steer))
        vehicle.apply_control(control)

        vt = vehicle.get_transform()
        spectator.set_transform(
            carla.Transform(
                vt.location + vt.get_forward_vector() * -8 + carla.Location(z=3),
                carla.Rotation(pitch=-10, yaw=vt.rotation.yaw)))

        v = vehicle.get_velocity()
        speed = 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)

        if i % 10 == 0:
            print(f"Frame: {i:3d} | Throttle: {control.throttle:.2f} | "
                  f"Steer: {control.steer:.2f} | Speed: {speed:.1f} km/h")

        time.sleep(0.05)

finally:
    control = carla.VehicleControl()
    control.brake = 1.0
    vehicle.apply_control(control)
    time.sleep(0.5)
    vehicle.destroy()
