import carla
import time
import numpy as np
import cv2
import os

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
bp_lib = world.get_blueprint_library()

vehicle_bp = bp_lib.filter('model3')[0]
spawn_point = world.get_map().get_spawn_points()[0]
vehicle = world.spawn_actor(vehicle_bp, spawn_point)

camera_bp = bp_lib.find('sensor.camera.rgb')
camera_bp.set_attribute('image_size_x', '800')
camera_bp.set_attribute('image_size_y', '600')
camera_bp.set_attribute('fov', '90')

camera_transform = carla.Transform(
    carla.Location(x=1.5, z=2.4),
    carla.Rotation(pitch=0)
)
camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

image_data = [None]

def on_image(image):
    arr = np.frombuffer(image.raw_data, dtype=np.uint8)
    arr = arr.reshape((image.height, image.width, 4))
    image_data[0] = arr[:, :, :3]

camera.listen(on_image)

weather_presets = [
    (carla.WeatherParameters.ClearNoon, "ClearNoon"),
    (carla.WeatherParameters.CloudyNoon, "CloudyNoon"),
    (carla.WeatherParameters.WetNoon, "WetNoon"),
    (carla.WeatherParameters.WetCloudyNoon, "WetCloudyNoon"),
    (carla.WeatherParameters.SoftRainNoon, "SoftRainNoon"),
    (carla.WeatherParameters.MidRainyNoon, "MidRainyNoon"),
    (carla.WeatherParameters.HardRainNoon, "HardRainNoon"),
    (carla.WeatherParameters.ClearSunset, "ClearSunset"),
]

spectator = world.get_spectator()

for weather, name in weather_presets:
    world.set_weather(weather)
    time.sleep(1)

    vt = vehicle.get_transform()
    spectator.set_transform(
        carla.Transform(
            vt.location + carla.Location(z=30),
            carla.Rotation(pitch=-90)))

    if image_data[0] is not None:
        os.makedirs('weather_captures', exist_ok=True)
        cv2.imwrite(f'weather_captures/{name}.png', image_data[0])
        print(f"Saved: {name}")

    time.sleep(0.5)

camera.stop()
camera.destroy()
vehicle.destroy()
print("Done")
