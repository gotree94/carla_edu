import carla
import time

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)

world = client.get_world()
blueprint_library = world.get_blueprint_library()

vehicle_bp = blueprint_library.filter('model3')[0]
spawn_points = world.get_map().get_spawn_points()

if not spawn_points:
    print("No spawn points available")
    exit()

spawn_point = spawn_points[0]
vehicle = world.spawn_actor(vehicle_bp, spawn_point)
print(f"Vehicle spawned: {vehicle.type_id} at {spawn_point.location}")

spectator = world.get_spectator()
spectator.set_transform(
    carla.Transform(
        spawn_point.location + carla.Location(z=50),
        carla.Rotation(pitch=-90)
    ))

print("Running simulation for 5 seconds...")
time.sleep(5)

vehicle.destroy()
print("Done")
