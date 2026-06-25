CARLA_HOST = 'localhost'
CARLA_PORT = 2000
CARLA_TIMEOUT = 10.0

IMAGE_W = 640
IMAGE_H = 480
FOV = 90

CAMERA_POSITIONS = [
    ("Front Center", (1.5, 0, 2.4), (0, 0, 0), 90),
    ("Front Left",   (1.5, 0, 2.4), (0, 45, 0), 90),
    ("Front Right",  (1.5, 0, 2.4), (0, -45, 0), 90),
    ("Left B pillar",(1.5, 0, 2.4), (0, 90, 0), 90),
    ("Right B pillar",(1.5, 0, 2.4), (0, -90, 0), 90),
    ("Rear Center",  (-1.5, 0, 2.4), (0, 180, 0), 90),
    ("Rear Left",    (-1.5, 0, 2.4), (0, 135, 0), 90),
    ("Rear Right",   (-1.5, 0, 2.4), (0, -135, 0), 90),
]

TARGET_SPEED = 30.0

STEER_PID = {'kp': 0.8, 'ki': 0.05, 'kd': 0.1}
SPEED_PID = {'kp': 0.5, 'ki': 0.1, 'kd': 0.0}

SAVE_DIR = 'captures'
LOG_DIR = 'logs'
