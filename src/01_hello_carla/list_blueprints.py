import carla

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
bp_lib = world.get_blueprint_library()

print("=== Vehicle Blueprints ===")
for bp in bp_lib.filter('vehicle.*'):
    print(f"  {bp.id}")

print("\n=== Sensor Blueprints ===")
for bp in bp_lib.filter('sensor.*'):
    print(f"  {bp.id}")

print("\n=== All Maps ===")
for m in client.get_available_maps():
    print(f"  {m}")

print(f"\nTotal spawn points: {len(world.get_map().get_spawn_points())}")
