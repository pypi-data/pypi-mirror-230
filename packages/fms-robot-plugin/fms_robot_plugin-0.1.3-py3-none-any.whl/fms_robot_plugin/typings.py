from pydantic import BaseModel


class Vector3(BaseModel):
    """
    Based on ROS geometry_msgs/Vector3
    """

    x: float
    y: float
    z: float


class Twist(BaseModel):
    """
    Based on ROS geometry_msgs/Twist
    """

    linear: Vector3
    angular: Vector3


class LaserScan(BaseModel):
    """
    Based on ROS sensor_msgs/LaserScan
    """

    angle_min: float
    angle_max: float
    angle_increment: float
    time_increment: float
    scan_time: float
    range_min: float
    range_max: float
    ranges: list[float]
    intensities: list[float]
