import os
import sys
import webview
from ursina import *
import random
import math
import time as system_time

# ============================================================
# CONFIGURATION
# ============================================================

class DroneConfig:

    WORLD_SIZE = 140

    GROUND_Y = 0
    START_ALTITUDE = 8

    GRAVITY = 9.81

    MAX_LIFT_ACCEL = 19.62
    MAX_SPEED = 28

    AIR_DRAG = 0.55
    HORIZONTAL_ACCEL = 13.0

    YAW_RATE = 65.0
    PITCH_RATE = 48.0
    ROLL_RATE = 48.0

    CRASH_DESCENT_SPEED = 4.5
    CRASH_TILT_DEG = 15.0

    MAX_BATTERY = 100.0

    LOW_BATTERY_WARNING = 20.0
    CRITICAL_BATTERY = 8.0

    RING_SCORE = 100
    LANDING_SCORE = 250

    DRONE_RADIUS = 0.85

    MAX_ALTITUDE = 60.0

    WEATHER_WIND_LIMIT = 12.0

    CAMERA_CHASE_DISTANCE = 14
    CAMERA_CHASE_HEIGHT = 7

    FPV_OFFSET = 0.65

    ORBIT_HEIGHT = 24


# ============================================================
# BASIC UTILITY FUNCTIONS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def clamp01(value):
    return clamp(value, 0.0, 1.0)


def lerp_value(a, b, amount):
    amount = clamp01(amount)
    return a + (b - a) * amount


def normalize_angle(angle):
    return (angle + 180.0) % 360.0 - 180.0


def angle_difference(a, b):
    return normalize_angle(a - b)


def distance_2d(a, b):
    dx = a.x - b.x
    dz = a.z - b.z
    return math.sqrt(dx * dx + dz * dz)


def distance_3d(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z

    return math.sqrt(
        dx * dx +
        dy * dy +
        dz * dz
    )


def vector_magnitude(vector):
    return math.sqrt(
        vector.x * vector.x +
        vector.y * vector.y +
        vector.z * vector.z
    )


def safe_normalize(vector):
    magnitude = vector_magnitude(vector)

    if magnitude <= 0.0001:
        return Vec3(0, 0, 0)

    return vector / magnitude


def degrees_to_vector(angle):
    radians = math.radians(angle)

    return Vec3(
        math.sin(radians),
        0,
        math.cos(radians)
    )


def calculate_heading(direction):
    if vector_magnitude(direction) <= 0.0001:
        return 0.0

    return math.degrees(
        math.atan2(direction.x, direction.z)
    )


# ============================================================
# RANDOM / PROCEDURAL UTILITIES
# ============================================================

class RandomGenerator:

    def __init__(self, seed=None):
        self.generator = random.Random(seed)

    def float(self, minimum, maximum):
        return self.generator.uniform(
            minimum,
            maximum
        )

    def integer(self, minimum, maximum):
        return self.generator.randint(
            minimum,
            maximum
        )

    def choice(self, values):
        if not values:
            return None

        return self.generator.choice(values)

    def chance(self, probability):
        return self.generator.random() < probability

    def vector2(self, minimum, maximum):
        return (
            self.float(minimum, maximum),
            self.float(minimum, maximum)
        )

    def vector3(self, minimum, maximum):
        return Vec3(
            self.float(minimum, maximum),
            self.float(minimum, maximum),
            self.float(minimum, maximum)
        )


# ============================================================
# TELEMETRY
# ============================================================

class Telemetry:

    def __init__(self):

        self.altitude = 0.0
        self.speed = 0.0

        self.vertical_speed = 0.0
        self.horizontal_speed = 0.0

        self.heading = 0.0

        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0

        self.throttle = 0.0

        self.battery = 100.0

        self.wind_speed = 0.0
        self.wind_direction = 0.0

        self.flight_time = 0.0

        self.distance_travelled = 0.0

        self.g_force = 1.0

        self.signal_strength = 100.0

        self.gps_accuracy = 1.0

    def update(
        self,
        position,
        velocity,
        pitch,
        roll,
        yaw,
        throttle,
        battery,
        delta_time
    ):

        self.altitude = max(
            0.0,
            position.y
        )

        self.speed = vector_magnitude(
            velocity
        )

        self.vertical_speed = velocity.y

        self.horizontal_speed = math.sqrt(
            velocity.x ** 2 +
            velocity.z ** 2
        )

        self.heading = normalize_angle(yaw)

        self.pitch = pitch
        self.roll = roll
        self.yaw = yaw

        self.throttle = throttle

        self.battery = battery

        self.flight_time += delta_time

        self.distance_travelled += (
            self.speed * delta_time
        )

    def calculate_g_force(self, acceleration):

        self.g_force = (
            vector_magnitude(acceleration)
            / DroneConfig.GRAVITY
        )

        return self.g_force

    def update_signal(self, distance):

        signal_loss = distance / 100.0

        self.signal_strength = clamp(
            100.0 - signal_loss * 100.0,
            5.0,
            100.0
        )

        return self.signal_strength


# ============================================================
# BATTERY MANAGEMENT
# ============================================================

class BatterySystem:

    def __init__(self):

        self.capacity = DroneConfig.MAX_BATTERY

        self.level = self.capacity

        self.consumption_rate = 0.08

        self.flight_consumption = 0.0

        self.warning_triggered = False

        self.critical_triggered = False

    def reset(self):

        self.level = self.capacity

        self.warning_triggered = False
        self.critical_triggered = False

        self.flight_consumption = 0.0

    def calculate_consumption(
        self,
        throttle,
        speed,
        wind_speed
    ):

        base_consumption = 0.025

        throttle_consumption = (
            throttle * 0.09
        )

        speed_consumption = (
            speed / DroneConfig.MAX_SPEED
        ) * 0.035

        wind_consumption = (
            wind_speed / DroneConfig.WEATHER_WIND_LIMIT
        ) * 0.025

        return (
            base_consumption +
            throttle_consumption +
            speed_consumption +
            wind_consumption
        )

    def update(
        self,
        throttle,
        speed,
        wind_speed,
        delta_time
    ):

        consumption = self.calculate_consumption(
            throttle,
            speed,
            wind_speed
        )

        amount = (
            consumption * delta_time
        )

        self.level = clamp(
            self.level - amount,
            0.0,
            self.capacity
        )

        self.flight_consumption += amount

        if self.level <= DroneConfig.LOW_BATTERY_WARNING:
            self.warning_triggered = True

        if self.level <= DroneConfig.CRITICAL_BATTERY:
            self.critical_triggered = True

        return self.level

    def is_low(self):
        return (
            self.level <=
            DroneConfig.LOW_BATTERY_WARNING
        )

    def is_critical(self):
        return (
            self.level <=
            DroneConfig.CRITICAL_BATTERY
        )


# ============================================================
# WEATHER SYSTEM
# ============================================================

class WeatherSystem:

    WEATHER_TYPES = [
        "CLEAR",
        "LIGHT WIND",
        "CROSS WIND",
        "STRONG WIND",
        "CALM"
    ]

    def __init__(self, seed=42):

        self.random = RandomGenerator(seed)

        self.weather = "CLEAR"

        self.wind_speed = 0.0
        self.wind_direction = 0.0

        self.temperature = 28.0

        self.visibility = 100.0

        self.humidity = 55.0

        self.turbulence = 0.0

    def generate_weather(self):

        self.weather = self.random.choice(
            self.WEATHER_TYPES
        )

        if self.weather == "CLEAR":

            self.wind_speed = self.random.float(
                0.0,
                2.0
            )

            self.visibility = 100.0

            self.turbulence = 0.05

        elif self.weather == "LIGHT WIND":

            self.wind_speed = self.random.float(
                2.0,
                5.0
            )

            self.visibility = 95.0

            self.turbulence = 0.15

        elif self.weather == "CROSS WIND":

            self.wind_speed = self.random.float(
                4.0,
                8.0
            )

            self.visibility = 90.0

            self.turbulence = 0.30

        elif self.weather == "STRONG WIND":

            self.wind_speed = self.random.float(
                8.0,
                12.0
            )

            self.visibility = 75.0

            self.turbulence = 0.55

        else:

            self.wind_speed = 0.2

            self.visibility = 100.0

            self.turbulence = 0.01

        self.wind_direction = self.random.float(
            0,
            360
        )

        self.temperature = self.random.float(
            20,
            36
        )

        self.humidity = self.random.float(
            40,
            85
        )

    def get_wind_vector(self):

        return degrees_to_vector(
            self.wind_direction
        ) * self.wind_speed

    def apply_wind(self, velocity):

        wind = self.get_wind_vector()

        return velocity + (
            wind * 0.01
        )

    def turbulence_offset(self):

        return Vec3(
            random.uniform(
                -self.turbulence,
                self.turbulence
            ),
            random.uniform(
                -self.turbulence,
                self.turbulence
            ),
            random.uniform(
                -self.turbulence,
                self.turbulence
            )
        )


# ============================================================
# FLIGHT LOGGER
# ============================================================

class FlightLogger:

    def __init__(self):

        self.events = []

        self.telemetry_samples = []

        self.start_time = None

    def start(self):

        self.start_time = system_time.time()

        self.events.clear()
        self.telemetry_samples.clear()

        self.log_event(
            "FLIGHT SESSION STARTED"
        )

    def log_event(self, message):

        self.events.append({
            "time": system_time.time(),
            "message": message
        })

    def record_telemetry(self, telemetry):

        self.telemetry_samples.append({
            "altitude": telemetry.altitude,
            "speed": telemetry.speed,
            "battery": telemetry.battery,
            "heading": telemetry.heading
        })

    def get_event_count(self):

        return len(self.events)

    def get_sample_count(self):

        return len(self.telemetry_samples)

    def export_summary(self):

        return {
            "events": self.get_event_count(),
            "samples": self.get_sample_count()
        }


# ============================================================
# MISSION SYSTEM
# ============================================================

class MissionManager:

    def __init__(self):

        self.mission_name = (
            "DRONE OPS TRAINING"
        )

        self.current_stage = 0

        self.total_stages = 4

        self.completed = False

        self.failed = False

        self.stage_names = [
            "TAKEOFF",
            "RING NAVIGATION",
            "PRECISION LANDING",
            "RETURN TO BASE"
        ]

    def reset(self):

        self.current_stage = 0

        self.completed = False
        self.failed = False

    def advance(self):

        if self.completed:
            return

        self.current_stage += 1

        if (
            self.current_stage >=
            self.total_stages
        ):

            self.current_stage = (
                self.total_stages
            )

            self.completed = True

    def fail(self):

        self.failed = True

    def get_current_stage_name(self):

        index = self.current_stage

        if index >= len(
            self.stage_names
        ):
            index = len(
                self.stage_names
            ) - 1

        return self.stage_names[index]

    def progress(self):

        return (
            self.current_stage /
            self.total_stages
        )


# ============================================================
# NAVIGATION SYSTEM
# ============================================================

class NavigationSystem:

    def __init__(self):

        self.target = None

        self.distance_to_target = 0.0

        self.bearing = 0.0

        self.altitude_difference = 0.0

    def set_target(self, target):

        self.target = target

    def clear_target(self):

        self.target = None

    def update(self, drone_position):

        if self.target is None:

            self.distance_to_target = 0.0
            self.bearing = 0.0
            self.altitude_difference = 0.0

            return

        direction = (
            self.target -
            drone_position
        )

        self.distance_to_target = (
            vector_magnitude(direction)
        )

        self.bearing = calculate_heading(
            direction
        )

        self.altitude_difference = (
            self.target.y -
            drone_position.y
        )

    def is_near_target(self, radius=4.0):

        return (
            self.distance_to_target <=
            radius
        )


# ============================================================
# SAFETY MONITOR
# ============================================================

class SafetyMonitor:

    def __init__(self):

        self.warnings = []

        self.last_warning = ""

        self.collision_warning = False

        self.low_battery_warning = False

        self.high_speed_warning = False

        self.high_altitude_warning = False

    def reset(self):

        self.warnings.clear()

        self.last_warning = ""

        self.collision_warning = False
        self.low_battery_warning = False
        self.high_speed_warning = False
        self.high_altitude_warning = False

    def add_warning(self, message):

        self.last_warning = message

        self.warnings.append(message)

    def check_speed(self, speed):

        self.high_speed_warning = (
            speed >
            DroneConfig.MAX_SPEED * 0.9
        )

        if self.high_speed_warning:

            self.add_warning(
                "HIGH SPEED"
            )

    def check_altitude(self, altitude):

        self.high_altitude_warning = (
            altitude >
            DroneConfig.MAX_ALTITUDE
        )

        if self.high_altitude_warning:

            self.add_warning(
                "ALTITUDE LIMIT"
            )

    def check_battery(self, battery):

        self.low_battery_warning = (
            battery <=
            DroneConfig.LOW_BATTERY_WARNING
        )

        if self.low_battery_warning:

            self.add_warning(
                "LOW BATTERY"
            )

    def safety_status(self):

        if (
            self.collision_warning or
            self.low_battery_warning or
            self.high_speed_warning or
            self.high_altitude_warning
        ):

            return "WARNING"

        return "NORMAL"


# ============================================================
# WORLD GENERATOR
# ============================================================

class WorldGenerator:

    def __init__(self, seed=42):

        self.random = RandomGenerator(seed)

        self.buildings = []

        self.roads = []

        self.decorations = []

    def random_position(self):

        return Vec3(
            self.random.float(-60, 60),
            0,
            self.random.float(-60, 60)
        )

    def valid_building_position(
        self,
        position
    ):

        if (
            abs(position.x) < 13 and
            abs(position.z) < 13
        ):

            return False

        if (
            abs(position.x) < 5 or
            abs(position.z) < 5
        ):

            return False

        return True

    def generate_building_data(self):

        position = self.random_position()

        while not self.valid_building_position(
            position
        ):

            position = self.random_position()

        width = self.random.float(4, 9)

        depth = self.random.float(4, 9)

        height = self.random.float(5, 22)

        return {
            "position": position,
            "width": width,
            "depth": depth,
            "height": height
        }

    def generate_buildings(
        self,
        amount=30
    ):

        self.buildings.clear()

        for _ in range(amount):

            data = (
                self.generate_building_data()
            )

            self.buildings.append(data)

        return self.buildings

    def generate_road_data(self):

        return {
            "width": 7,
            "length": DroneConfig.WORLD_SIZE,
            "surface": "asphalt"
        }

    def generate_environment(self):

        return {
            "buildings":
                self.generate_buildings(),

            "road":
                self.generate_road_data()
        }


# ============================================================
# LANDING PAD DATA
# ============================================================

class LandingPadData:

    def __init__(
        self,
        name,
        position
    ):

        self.name = name

        self.position = position

        self.radius = 3.6

        self.required_speed = 2.0

        self.max_tilt = (
            DroneConfig.CRASH_TILT_DEG
        )

        self.successful_landings = 0

    def check_position(
        self,
        drone_position
    ):

        horizontal_distance = math.sqrt(
            (
                drone_position.x -
                self.position.x
            ) ** 2
            +
            (
                drone_position.z -
                self.position.z
            ) ** 2
        )

        return (
            horizontal_distance <
            self.radius
        )

    def register_landing(self):

        self.successful_landings += 1


# ============================================================
# TRAINING RING DATA
# ============================================================

class TrainingRing:

    def __init__(
        self,
        ring_id,
        position
    ):

        self.ring_id = ring_id

        self.position = position

        self.radius = 3.6

        self.passed = False

        self.score = (
            DroneConfig.RING_SCORE
        )

    def check_passage(
        self,
        drone_position
    ):

        if self.passed:
            return False

        if (
            distance_3d(
                drone_position,
                self.position
            )
            <
            self.radius
        ):

            self.passed = True

            return True

        return False

    def reset(self):

        self.passed = False


# ============================================================
# DRONE FLIGHT CONTROLLER
# ============================================================

class FlightController:

    def __init__(self):

        self.throttle = 0.50

        self.pitch_input = 0.0

        self.roll_input = 0.0

        self.yaw_input = 0.0

        self.velocity = Vec3(
            0,
            0,
            0
        )

        self.drone_yaw = 0.0

        self.drone_pitch = 0.0

        self.drone_roll = 0.0

    def reset(self):

        self.throttle = 0.50

        self.pitch_input = 0.0
        self.roll_input = 0.0
        self.yaw_input = 0.0

        self.velocity = Vec3(
            0,
            0,
            0
        )

        self.drone_yaw = 0.0
        self.drone_pitch = 0.0
        self.drone_roll = 0.0

    def update_inputs(
        self,
        keys
    ):

        if "space" in keys:

            self.throttle += (
                0.35 * 0.016
            )

        if "shift" in keys:

            self.throttle -= (
                0.35 * 0.016
            )

        self.throttle = clamp01(
            self.throttle
        )

        self.pitch_input = 0
        self.roll_input = 0
        self.yaw_input = 0

        if "w" in keys:
            self.pitch_input += 1

        if "s" in keys:
            self.pitch_input -= 1

        if "a" in keys:
            self.roll_input -= 1

        if "d" in keys:
            self.roll_input += 1

        if "q" in keys:
            self.yaw_input -= 1

        if "e" in keys:
            self.yaw_input += 1

    def calculate_forward(self):

        return degrees_to_vector(
            self.drone_yaw
        )

    def calculate_right(self):

        yaw = math.radians(
            self.drone_yaw
        )

        return Vec3(
            math.cos(yaw),
            0,
            -math.sin(yaw)
        )

    def calculate_lift(self):

        pitch_rad = math.radians(
            self.drone_pitch
        )

        roll_rad = math.radians(
            self.drone_roll
        )

        horizontal_forward = (
            math.sin(pitch_rad)
        )

        horizontal_right = (
            math.sin(roll_rad)
        )

        forward = (
            self.calculate_forward()
        )

        right = (
            self.calculate_right()
        )

        horizontal = (
            forward *
            horizontal_forward
            +
            right *
            horizontal_right
        )

        horizontal *= (
            DroneConfig.MAX_LIFT_ACCEL
            *
            self.throttle
        )

        vertical = (
            DroneConfig.MAX_LIFT_ACCEL
            *
            self.throttle
            *
            math.cos(pitch_rad)
            *
            math.cos(roll_rad)
        )

        return Vec3(
            horizontal.x,
            vertical,
            horizontal.z
        )

    def calculate_acceleration(
        self,
        weather=None
    ):

        lift = self.calculate_lift()

        gravity = Vec3(
            0,
            -DroneConfig.GRAVITY,
            0
        )

        drag = (
            self.velocity *
            DroneConfig.AIR_DRAG
        )

        acceleration = (
            lift +
            gravity -
            drag
        )

        if weather is not None:

            wind = (
                weather.get_wind_vector()
            )

            acceleration += (
                wind * 0.02
            )

        return acceleration

    def update_attitude(
        self,
        delta_time
    ):

        self.drone_pitch = lerp(
            self.drone_pitch,
            self.pitch_input *
            DroneConfig.PITCH_RATE,
            min(
                1,
                delta_time * 5
            )
        )

        self.drone_roll = lerp(
            self.drone_roll,
            self.roll_input *
            DroneConfig.ROLL_RATE,
            min(
                1,
                delta_time * 5
            )
        )

        self.drone_yaw += (
            self.yaw_input *
            DroneConfig.YAW_RATE *
            delta_time
        )


# ============================================================
# SCORE SYSTEM
# ============================================================

class ScoreSystem:

    def __init__(self):

        self.score = 0

        self.ring_score = 100

        self.landing_score = 250

        self.bonus_score = 0

        self.penalty_score = 0

    def reset(self):

        self.score = 0
        self.bonus_score = 0
        self.penalty_score = 0

    def add_ring_score(self):

        self.score += self.ring_score

    def add_landing_score(self):

        self.score += self.landing_score

    def add_bonus(self, amount):

        amount = max(
            0,
            amount
        )

        self.bonus_score += amount

        self.score += amount

    def add_penalty(self, amount):

        amount = max(
            0,
            amount
        )

        self.penalty_score += amount

        self.score = max(
            0,
            self.score - amount
        )

    def get_final_score(self):

        return self.score


# ============================================================
# CAMERA MANAGER
# ============================================================

class CameraManager:

    MODES = [
        "CHASE",
        "FPV",
        "ORBIT"
    ]

    def __init__(self):

        self.mode = 0

        self.smoothing = 4.0

    def cycle(self):

        self.mode = (
            self.mode + 1
        ) % len(self.MODES)

    def current_mode(self):

        return self.MODES[
            self.mode
        ]

    def chase_position(
        self,
        drone_position,
        yaw
    ):

        yaw_rad = math.radians(yaw)

        back = Vec3(
            -math.sin(yaw_rad) * 14,
            7,
            -math.cos(yaw_rad) * 14
        )

        return (
            drone_position
            +
            Vec3(0, 3.5, 0)
            +
            back
        )

    def orbit_position(
        self,
        drone_position
    ):

        return (
            drone_position
            +
            Vec3(0, 24, -0.1)
        )


# ============================================================
# COLLISION SYSTEM
# ============================================================

class CollisionSystem:

    def __init__(self):

        self.last_collision = None

        self.collision_count = 0

    def reset(self):

        self.last_collision = None

        self.collision_count = 0

    def check_building_collision(
        self,
        drone_position,
        building_data
    ):

        position = building_data[
            "position"
        ]

        half_x = (
            building_data["width"] / 2
            +
            DroneConfig.DRONE_RADIUS
        )

        half_z = (
            building_data["depth"] / 2
            +
            DroneConfig.DRONE_RADIUS
        )

        if (
            abs(
                drone_position.x -
                position.x
            )
            <
            half_x
            and
            abs(
                drone_position.z -
                position.z
            )
            <
            half_z
        ):

            bottom = 0

            top = (
                building_data["height"]
            )

            if (
                bottom <=
                drone_position.y <=
                top
            ):

                self.last_collision = (
                    "BUILDING"
                )

                self.collision_count += 1

                return True

        return False

    def check_world_boundary(
        self,
        position
    ):

        margin = (
            DroneConfig.WORLD_SIZE / 2
            - 2
        )

        return (
            abs(position.x) > margin
            or
            abs(position.z) > margin
        )


# ============================================================
# FLIGHT STATE
# ============================================================

class FlightState:

    READY = "READY"
    FLYING = "FLYING"
    HOVER = "HOVER"
    LANDED = "LANDED"
    CRASHED = "CRASHED"
    RETURNING = "RETURNING"
    LOW_BATTERY = "LOW BATTERY"


# ============================================================
# DRONE STATE MANAGER
# ============================================================

class DroneStateManager:

    def __init__(self):

        self.state = (
            FlightState.READY
        )

        self.crash_reason = ""

        self.landing_location = ""

    def reset(self):

        self.state = (
            FlightState.READY
        )

        self.crash_reason = ""

        self.landing_location = ""

    def set_flying(self):

        self.state = (
            FlightState.FLYING
        )

    def set_hovering(self):

        self.state = (
            FlightState.HOVER
        )

    def set_landed(self, pad_name):

        self.state = (
            FlightState.LANDED
        )

        self.landing_location = (
            pad_name
        )

    def set_crashed(self, reason):

        self.state = (
            FlightState.CRASHED
        )

        self.crash_reason = reason

    def set_returning(self):

        self.state = (
            FlightState.RETURNING
        )


# ============================================================
# MISSION ROUTE GENERATOR
# ============================================================

class MissionRouteGenerator:

    def __init__(self, seed=100):

        self.random = RandomGenerator(seed)

        self.route = []

    def generate_route(
        self,
        count=8
    ):

        self.route.clear()

        for index in range(count):

            position = Vec3(
                self.random.float(
                    -50,
                    50
                ),
                self.random.float(
                    8,
                    25
                ),
                self.random.float(
                    -50,
                    50
                )
            )

            self.route.append({
                "id": index + 1,
                "position": position,
                "completed": False
            })

        return self.route

    def reset_route(self):

        for waypoint in self.route:

            waypoint["completed"] = False

    def mark_completed(self, waypoint_id):

        for waypoint in self.route:

            if (
                waypoint["id"] ==
                waypoint_id
            ):

                waypoint[
                    "completed"
                ] = True


# ============================================================
# FLIGHT ANALYTICS
# ============================================================

class FlightAnalytics:

    def __init__(self):

        self.max_altitude = 0.0

        self.max_speed = 0.0

        self.max_g_force = 1.0

        self.total_distance = 0.0

        self.average_speed = 0.0

        self.samples = 0

    def update(
        self,
        telemetry
    ):

        self.max_altitude = max(
            self.max_altitude,
            telemetry.altitude
        )

        self.max_speed = max(
            self.max_speed,
            telemetry.speed
        )

        self.max_g_force = max(
            self.max_g_force,
            telemetry.g_force
        )

        self.total_distance = (
            telemetry.distance_travelled
        )

        self.samples += 1

        if self.samples > 0:

            self.average_speed = (
                self.average_speed *
                (self.samples - 1)
                +
                telemetry.speed
            ) / self.samples

    def generate_report(self):

        return {
            "maximum_altitude":
                self.max_altitude,

            "maximum_speed":
                self.max_speed,

            "maximum_g_force":
                self.max_g_force,

            "total_distance":
                self.total_distance,

            "average_speed":
                self.average_speed
        }


# ============================================================
# PROCEDURAL ENVIRONMENT HELPERS
# ============================================================

def generate_building_color():

    return color.rgb(
        random.randint(105, 180),
        random.randint(105, 180),
        random.randint(110, 190)
    )


def create_building_entity(
    data
):

    return Entity(
        model="cube",
        position=(
            data["position"].x,
            data["height"] / 2,
            data["position"].z
        ),
        scale=(
            data["width"],
            data["height"],
            data["depth"]
        ),
        color=generate_building_color(),
        collider="box"
    )


def create_roof_marker(
    building
):

    return Entity(
        model="cube",
        position=(
            building.x,
            building.y +
            building.scale_y / 2 +
            0.08,
            building.z
        ),
        scale=(
            building.scale_x * 0.55,
            0.12,
            building.scale_z * 0.55
        ),
        color=color.rgb(
            55,
            55,
            60
        )
    )


def create_landing_pad(
    name,
    position
):

    pad = Entity(
        model="cube",
        position=position,
        scale=(9, 0.15, 9),
        color=color.rgb(
            55,
            55,
            55
        )
    )

    Entity(
        model="cube",
        position=(
            position[0],
            position[1] + 0.09,
            position[2]
        ),
        scale=(
            7.5,
            0.05,
            7.5
        ),
        color=color.rgb(
            225,
            225,
            225
        )
    )

    Text(
        text=name,
        parent=pad,
        y=0.09,
        scale=2.5,
        origin=(0, 0),
        color=color.orange
    )

    return pad


def create_training_ring(
    position,
    ring_id
):

    ring = Entity(
        model="torus",
        position=position,
        scale=4.0,
        color=color.orange,
        double_sided=True
    )

    ring.ring_id = ring_id

    ring.passed = False

    Text(
        text=str(ring_id + 1),
        parent=ring,
        y=1.25,
        scale=1.5,
        origin=(0, 0),
        color=color.white
    )

    return ring


# ============================================================
# DRONE VISUAL MODEL
# ============================================================

def create_drone_model():

    drone = Entity(
        model="cube",
        position=(
            0,
            DroneConfig.START_ALTITUDE,
            0
        ),
        scale=(
            1.5,
            0.28,
            1.5
        ),
        color=color.rgb(
            35,
            35,
            42
        )
    )

    Entity(
        parent=drone,
        model="cube",
        scale=(
            0.18,
            0.16,
            2.8
        ),
        color=color.rgb(
            70,
            70,
            75
        )
    )

    Entity(
        parent=drone,
        model="cube",
        scale=(
            2.8,
            0.16,
            0.18
        ),
        color=color.rgb(
            70,
            70,
            75
        )
    )

    rotors = []

    rotor_positions = [
        (-1.0, -1.0),
        (1.0, -1.0),
        (-1.0, 1.0),
        (1.0, 1.0)
    ]

    for x, z in rotor_positions:

        motor = Entity(
            parent=drone,
            model="cylinder",
            position=(
                x,
                0.15,
                z
            ),
            scale=(
                0.28,
                0.16,
                0.28
            ),
            color=color.rgb(
                25,
                25,
                28
            )
        )

        rotor = Entity(
            parent=motor,
            model="cube",
            position=(
                0,
                0.12,
                0
            ),
            scale=(
                0.9,
                0.035,
                0.08
            ),
            color=color.rgb(
                220,
                220,
                220
            )
        )

        rotors.append(rotor)

    Entity(
        parent=drone,
        model="cube",
        position=(
            0,
            0.18,
            0.85
        ),
        scale=(
            0.35,
            0.08,
            0.15
        ),
        color=color.red
    )

    return drone, rotors


# ============================================================
# HUD CREATION
# ============================================================

def create_hud():

    hud = Text(
        text="",
        position=(-0.86, 0.45),
        origin=(-0.5, 0.5),
        scale=0.95,
        background=True
    )

    status_text = Text(
        text="READY",
        position=(0, 0.43),
        origin=(0, 0),
        scale=1.25,
        color=color.lime
    )

    help_text = Text(
        text=(
            "CONTROLS\n"
            "SPACE       Throttle up\n"
            "LEFT SHIFT  Throttle down\n"
            "W / S       Pitch\n"
            "A / D       Roll\n"
            "Q / E       Yaw\n"
            "R           Reset\n"
            "C           Camera\n"
            "H           Help\n"
            "ESC         Quit\n\n"
            "HOVER: ~50% THROTTLE"
        ),
        position=(0.53, 0.42),
        origin=(0, 0.5),
        scale=0.72,
        background=True
    )

    message_text = Text(
        text="",
        position=(0, -0.36),
        origin=(0, 0),
        scale=1.25,
        color=color.orange
    )

    return (
        hud,
        status_text,
        help_text,
        message_text
    )


# ============================================================
# ENVIRONMENT CREATION
# ============================================================

def create_environment():

    world = WorldGenerator(
        seed=42
    )

    Sky(
        color=color.rgb(
            145,
            205,
            235
        )
    )

    ground = Entity(
        model="plane",
        texture="white_cube",
        texture_scale=(
            DroneConfig.WORLD_SIZE / 4,
            DroneConfig.WORLD_SIZE / 4
        ),
        scale=(
            DroneConfig.WORLD_SIZE,
            1,
            DroneConfig.WORLD_SIZE
        ),
        color=color.rgb(
            72,
            125,
            72
        ),
        collider="box"
    )

    road1 = Entity(
        model="cube",
        scale=(
            DroneConfig.WORLD_SIZE,
            0.03,
            7
        ),
        y=0.02,
        color=color.rgb(
            75,
            75,
            75
        )
    )

    road2 = Entity(
        model="cube",
        scale=(
            7,
            0.03,
            DroneConfig.WORLD_SIZE
        ),
        y=0.021,
        color=color.rgb(
            75,
            75,
            75
        )
    )

    for i in range(
        -60,
        61,
        12
    ):

        Entity(
            model="cube",
            scale=(
                5,
                0.04,
                0.25
            ),
            position=(
                i,
                0.05,
                0
            ),
            color=color.rgb(
                225,
                225,
                180
            )
        )

        Entity(
            model="cube",
            scale=(
                0.25,
                0.04,
                5
            ),
            position=(
                0,
                0.051,
                i
            ),
            color=color.rgb(
                225,
                225,
                180
            )
        )

    buildings = []

    building_data = (
        world.generate_buildings(30)
    )

    for data in building_data:

        building = (
            create_building_entity(data)
        )

        buildings.append(building)

        create_roof_marker(
            building
        )

    return {
        "ground": ground,
        "road1": road1,
        "road2": road2,
        "buildings": buildings
    }


# ============================================================
# RING CREATION
# ============================================================

def create_training_course():

    ring_positions = [
        Vec3(-25, 12, -30),
        Vec3(-5, 18, -48),
        Vec3(25, 14, -38),
        Vec3(48, 20, -12),
        Vec3(35, 10, 18),
        Vec3(10, 16, 42),
        Vec3(-22, 13, 48),
        Vec3(-45, 20, 22)
    ]

    rings = []

    for index, position in enumerate(
        ring_positions
    ):

        ring = create_training_ring(
            position,
            index
        )

        rings.append(ring)

    return rings


# ============================================================
# SIMULATOR RUNTIME CLASS
# ============================================================

class DroneSimulator:

    def __init__(self):

        self.flight_controller = (
            FlightController()
        )

        self.telemetry = (
            Telemetry()
        )

        self.battery = (
            BatterySystem()
        )

        self.weather = (
            WeatherSystem()
        )

        self.logger = (
            FlightLogger()
        )

        self.mission = (
            MissionManager()
        )

        self.navigation = (
            NavigationSystem()
        )

        self.safety = (
            SafetyMonitor()
        )

        self.analytics = (
            FlightAnalytics()
        )

        self.score_system = (
            ScoreSystem()
        )

        self.collision = (
            CollisionSystem()
        )

        self.camera_manager = (
            CameraManager()
        )

        self.state_manager = (
            DroneStateManager()
        )

        self.route_generator = (
            MissionRouteGenerator()
        )

        self.keys_down = set()

        self.crashed = False

        self.landed = False

        self.elapsed = 0.0

    def reset(self):

        self.flight_controller.reset()

        self.battery.reset()

        self.mission.reset()

        self.navigation.clear_target()

        self.safety.reset()

        self.score_system.reset()

        self.collision.reset()

        self.state_manager.reset()

        self.route_generator.reset_route()

        self.crashed = False

        self.landed = False

        self.elapsed = 0.0

        self.logger.start()

    def crash(self, reason):

        if self.crashed:
            return

        self.crashed = True

        self.landed = False

        self.state_manager.set_crashed(
            reason
        )

        self.mission.fail()

        self.logger.log_event(
            "CRASH: " + reason
        )

    def process_landing(
        self,
        pad,
        drone_position
    ):

        if self.crashed:
            return False

        if not pad.check_position(
            drone_position
        ):
            return False

        speed = (
            self.flight_controller
            .velocity
            .length()
        )

        tilt = max(
            abs(
                self.flight_controller
                .drone_pitch
            ),
            abs(
                self.flight_controller
                .drone_roll
            )
        )

        if speed < 2.0 and tilt < pad.max_tilt:

            self.landed = True

            pad.register_landing()

            self.score_system.add_landing_score()

            self.state_manager.set_landed(
                pad.name
            )

            self.logger.log_event(
                "PRECISION LANDING: "
                + pad.name
            )

            return True

        return False

    def process_ring(
        self,
        ring,
        drone_position
    ):

        if ring.check_passage(
            drone_position
        ):

            self.score_system.add_ring_score()

            self.logger.log_event(
                "RING PASSED: "
                + str(ring.ring_id + 1)
            )

            return True

        return False

    def update_telemetry(
        self,
        position,
        delta_time
    ):

        controller = (
            self.flight_controller
        )

        self.telemetry.update(
            position,
            controller.velocity,
            controller.drone_pitch,
            controller.drone_roll,
            controller.drone_yaw,
            controller.throttle,
            self.battery.level,
            delta_time
        )

        self.telemetry.wind_speed = (
            self.weather.wind_speed
        )

        self.telemetry.wind_direction = (
            self.weather.wind_direction
        )

        self.analytics.update(
            self.telemetry
        )

        self.logger.record_telemetry(
            self.telemetry
        )

    def update_safety(self):

        self.safety.check_speed(
            self.telemetry.speed
        )

        self.safety.check_altitude(
            self.telemetry.altitude
        )

        self.safety.check_battery(
            self.telemetry.battery
        )

    def update_navigation(
        self,
        position
    ):

        self.navigation.update(
            position
        )

    def calculate_status(self):

        if self.crashed:

            return "CRASHED"

        if self.landed:

            return "LANDED"

        if self.battery.is_critical():

            return "LOW BATTERY"

        if (
            abs(
                self.flight_controller
                .throttle - 0.5
            ) < 0.04
            and
            self.telemetry.speed < 2.5
        ):

            return "HOVER"

        return "FLYING"


# ============================================================
# SIMULATOR BUILDER
# ============================================================

def build_simulator():

    """
    Creates the actual simulator.

    IMPORTANT:
    This function is intentionally NOT called automatically.
    """

    app = Ursina()

    window.title = (
        "Drone Flight Training Simulator"
    )

    window.borderless = False

    window.exit_button.visible = False

    window.fps_counter.enabled = True

    window.color = color.rgb(
        120,
        180,
        220
    )

    simulator = DroneSimulator()

    simulator.weather.generate_weather()

    environment = create_environment()

    drone, rotors = create_drone_model()

    rings = create_training_course()

    home_pad = create_landing_pad(
        "HOME",
        (0, 0.13, 0)
    )

    pad_b = create_landing_pad(
        "PAD B",
        (48, 0.13, 48)
    )

    hud, status_text, help_text, message_text = (
        create_hud()
    )

    return {
        "app": app,
        "simulator": simulator,
        "environment": environment,
        "drone": drone,
        "rotors": rotors,
        "rings": rings,
        "home_pad": home_pad,
        "pad_b": pad_b,
        "hud": hud,
        "status_text": status_text,
        "help_text": help_text,
        "message_text": message_text
    }


# ============================================================
# OPTIONAL DEVELOPMENT / TEST FUNCTIONS
# ============================================================

def run_physics_test():

    controller = FlightController()

    controller.throttle = 0.50

    controller.pitch_input = 0

    controller.roll_input = 0

    controller.yaw_input = 0

    acceleration = (
        controller.calculate_acceleration()
    )

    return {
        "throttle":
            controller.throttle,

        "acceleration":
            acceleration
    }


def run_weather_test():

    weather = WeatherSystem(
        seed=123
    )

    weather.generate_weather()

    return {
        "weather":
            weather.weather,

        "wind_speed":
            weather.wind_speed,

        "wind_direction":
            weather.wind_direction,

        "visibility":
            weather.visibility,

        "temperature":
            weather.temperature
    }


def run_navigation_test():

    navigation = NavigationSystem()

    navigation.set_target(
        Vec3(
            20,
            15,
            30
        )
    )

    navigation.update(
        Vec3(
            0,
            8,
            0
        )
    )

    return {
        "distance":
            navigation.distance_to_target,

        "bearing":
            navigation.bearing,

        "altitude_difference":
            navigation.altitude_difference
    }


def run_battery_test():

    battery = BatterySystem()

    initial = battery.level

    battery.update(
        throttle=0.65,
        speed=10.0,
        wind_speed=4.0,
        delta_time=10.0
    )

    return {
        "initial":
            initial,

        "remaining":
            battery.level
    }


def run_mission_test():

    mission = MissionManager()

    mission.reset()

    mission.advance()

    mission.advance()

    return {
        "stage":
            mission.get_current_stage_name(),

        "progress":
            mission.progress(),

        "completed":
            mission.completed
    }


# ============================================================
# DATA VALIDATION
# ============================================================

def validate_drone_configuration():

    errors = []

    if (
        DroneConfig.MAX_SPEED <= 0
    ):

        errors.append(
            "Invalid maximum speed"
        )

    if (
        DroneConfig.GRAVITY <= 0
    ):

        errors.append(
            "Invalid gravity"
        )

    if (
        DroneConfig.MAX_LIFT_ACCEL <= 0
    ):

        errors.append(
            "Invalid lift acceleration"
        )

    if (
        DroneConfig.WORLD_SIZE <= 0
    ):

        errors.append(
            "Invalid world size"
        )

    return errors


def validate_route(route):

    if not route:

        return False

    for waypoint in route:

        if "position" not in waypoint:
            return False

        if "id" not in waypoint:
            return False

    return True


# ============================================================
# PROCEDURAL MISSION DATA
# ============================================================

def generate_mission_brief():

    return {
        "mission":
            "DRONE OPS TRAINING",

        "objective":
            "Complete the training course",

        "secondary_objective":
            "Perform precision landing",

        "environment":
            "Urban training zone",

        "flight_mode":
            "Manual",

        "navigation":
            "Visual waypoint navigation",

        "safety":
            "Collision and battery monitoring"
    }


def generate_drone_specification():

    return {
        "vehicle":
            "Quadrotor",

        "control":
            "Manual",

        "maximum_speed":
            DroneConfig.MAX_SPEED,

        "maximum_altitude":
            DroneConfig.MAX_ALTITUDE,

        "lift_acceleration":
            DroneConfig.MAX_LIFT_ACCEL,

        "gravity_model":
            DroneConfig.GRAVITY,

        "air_drag":
            DroneConfig.AIR_DRAG,

        "yaw_rate":
            DroneConfig.YAW_RATE,

        "pitch_rate":
            DroneConfig.PITCH_RATE,

        "roll_rate":
            DroneConfig.ROLL_RATE
    }


# ============================================================
# PERFORMANCE CALCULATIONS
# ============================================================

def estimate_hover_power(
    throttle
):

    throttle = clamp01(
        throttle
    )

    return (
        throttle ** 1.5
    )


def estimate_flight_time(
    battery_percentage,
    average_throttle
):

    if average_throttle <= 0:

        return 0.0

    base_minutes = 25.0

    factor = (
        1.0 /
        max(
            0.1,
            average_throttle
        )
    )

    return (
        base_minutes *
        battery_percentage /
        100.0 *
        factor
    )


def calculate_turn_rate(
    yaw_input
):

    return (
        yaw_input *
        DroneConfig.YAW_RATE
    )


def calculate_tilt_energy(
    pitch,
    roll
):

    pitch_energy = (
        abs(pitch) /
        DroneConfig.PITCH_RATE
    )

    roll_energy = (
        abs(roll) /
        DroneConfig.ROLL_RATE
    )

    return (
        pitch_energy +
        roll_energy
    )


# ============================================================
# SIMULATION DATA EXPORT
# ============================================================

def create_simulation_summary(
    simulator
):

    return {
        "mission":
            simulator.mission.mission_name,

        "score":
            simulator.score_system.score,

        "battery":
            simulator.battery.level,

        "flight_time":
            simulator.telemetry.flight_time,

        "distance":
            simulator.telemetry.distance_travelled,

        "max_altitude":
            simulator.analytics.max_altitude,

        "max_speed":
            simulator.analytics.max_speed,

        "state":
            simulator.state_manager.state,

        "weather":
            simulator.weather.weather
    }


def format_telemetry(
    telemetry
):

    return (
        f"ALT {telemetry.altitude:5.1f} m | "
        f"SPD {telemetry.speed:5.1f} m/s | "
        f"BAT {telemetry.battery:5.1f}% | "
        f"HDG {telemetry.heading:6.1f}°"
    )


# ============================================================
# FUTURE EXTENSION HOOKS
# ============================================================

def load_audio_assets():

    """
    Placeholder for future audio integration.

    Possible assets:
        - rotor_idle.wav
        - rotor_high.wav
        - collision.wav
        - warning.wav
        - landing.wav
        - mission_complete.wav
    """

    return {
        "rotor_idle": None,
        "rotor_high": None,
        "collision": None,
        "warning": None,
        "landing": None,
        "mission_complete": None
    }


def load_environment_assets():

    """
    Placeholder for future environment assets.
    """

    return {
        "terrain": None,
        "trees": None,
        "buildings": None,
        "roads": None,
        "lights": None,
        "landing_pads": None
    }


def load_drone_assets():

    """
    Placeholder for future drone models.
    """

    return {
        "body": None,
        "propeller": None,
        "camera": None,
        "navigation_light": None
    }


def configure_graphics():

    """
    Future graphics configuration hook.
    """

    return {
        "shadows": True,
        "anti_aliasing": True,
        "dynamic_lighting": True,
        "environment_detail": "HIGH",
        "texture_quality": "HIGH"
    }


def configure_simulation():

    """
    Central configuration for future simulator versions.
    """

    return {
        "physics_enabled": True,
        "collision_enabled": True,
        "weather_enabled": True,
        "battery_enabled": True,
        "telemetry_enabled": True,
        "mission_system_enabled": True,
        "logging_enabled": True
    }


# ============================================================
# DEMONSTRATION DATA GENERATORS
# ============================================================

def generate_sample_telemetry():

    samples = []

    for index in range(20):

        altitude = (
            8 +
            math.sin(index * 0.3) * 4
        )

        speed = (
            5 +
            math.cos(index * 0.25) * 2
        )

        battery = (
            100 -
            index * 1.7
        )

        samples.append({
            "time": index,
            "altitude": altitude,
            "speed": speed,
            "battery": battery
        })

    return samples


def generate_training_statistics():

    return {
        "average_completion_time":
            0.0,

        "successful_landings":
            0,

        "rings_completed":
            0,

        "total_flights":
            0,

        "total_distance":
            0.0,

        "highest_altitude":
            0.0,

        "highest_speed":
            0.0
    }


# ============================================================
# FINAL SOURCE VALIDATION
# ============================================================

def source_health_check():

    checks = {
        "configuration":
            validate_drone_configuration(),

        "physics":
            run_physics_test(),

        "weather":
            run_weather_test(),

        "navigation":
            run_navigation_test(),

        "battery":
            run_battery_test(),

        "mission":
            run_mission_test()
    }

    return checks


def main():
    # Path to your HTML file
    html_file = os.path.abspath("DRONE__OPS.html")
    
    if not os.path.exists(html_file):
        print(f"Error: Could not find '{html_file}' in the current directory.")
        sys.exit(1)

    # Launch desktop window
    window = webview.create_window(
        title="DRONE // OPS",
        url=f"file://{html_file}",
        width=1280,
        height=720,
        resizable=True,
        fullscreen=False
    )
    
    # gui='cef' or 'qt' can be specified if needed
    webview.start()

if __name__ == "__main__":
    main()
