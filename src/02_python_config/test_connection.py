import carla
import sys

def test_carla_connection():
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(5.0)
        world = client.get_world()
        print(f"Connected to CARLA server")
        print(f"CARLA version: {client.get_client_version()}")
        print(f"Server version: {client.get_server_version()}")
        print(f"Current map: {world.get_map().name}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Make sure CarlaUE4.exe is running!")
        return False

if __name__ == '__main__':
    success = test_carla_connection()
    sys.exit(0 if success else 1)
