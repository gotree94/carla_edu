import math
import carla
from config import TARGET_SPEED, STEER_PID, SPEED_PID


class PID:
    def __init__(self, kp, ki, kd):
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


class VehicleController:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.steer_pid = PID(**STEER_PID)
        self.speed_pid = PID(**SPEED_PID)
        self.target_speed = TARGET_SPEED

    def follow_waypoint(self, target_location):
        vt = self.vehicle.get_transform()
        vl = vt.location

        dx = target_location.x - vl.x
        dy = target_location.y - vl.y
        target_yaw = math.degrees(math.atan2(dy, dx))
        current_yaw = vt.rotation.yaw

        angle_error = (target_yaw - current_yaw + 180) % 360 - 180
        steer = self.steer_pid.control(angle_error / 90.0)

        v = self.vehicle.get_velocity()
        current_speed = 3.6 * math.sqrt(v.x**2 + v.y**2 + v.z**2)
        speed_error = self.target_speed - current_speed
        throttle = self.speed_pid.control(speed_error)

        control = carla.VehicleControl()
        control.steer = max(-1.0, min(1.0, steer))
        control.throttle = max(0.0, min(1.0, throttle))

        if current_speed > self.target_speed * 1.1:
            control.brake = min(1.0, (current_speed - self.target_speed) / self.target_speed)
            control.throttle = 0.0

        self.vehicle.apply_control(control)
        return control

    def emergency_stop(self):
        control = carla.VehicleControl()
        control.brake = 1.0
        self.vehicle.apply_control(control)

    def reset(self):
        self.steer_pid.reset()
        self.speed_pid.reset()
