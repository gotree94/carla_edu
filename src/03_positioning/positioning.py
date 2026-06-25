import carla
import time

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
map = world.get_map()
bp_lib = world.get_blueprint_library()

spawn_points = map.get_spawn_points()
print(f"Total spawn points: {len(spawn_points)}")

for i, sp in enumerate(spawn_points[:10]):
    print(f"  [{i}] {sp.location} (yaw: {sp.rotation.yaw:.1f})")

vehicle_bp = bp_lib.filter('model3')[0]
vehicle = world.spawn_actor(vehicle_bp, spawn_points[5])
print(f"\nSpawned at: {vehicle.get_transform().location}")

spectator = world.get_spectator()
spectator.set_transform(
    carla.Transform(
        vehicle.get_transform().location + carla.Location(z=50),
        carla.Rotation(pitch=-90)
    ))

time.sleep(2)

for i, sp in enumerate(spawn_points[10:15]):
    vehicle.set_transform(sp)
    print(f"Teleported to [{i+10}]: {sp.location}")

    spectator.set_transform(
        carla.Transform(
            sp.location + carla.Location(z=30),
            carla.Rotation(pitch=-90)
        ))
    time.sleep(1)

vehicle.destroy()
print("Done")
