import math


def get_delay_in_samples(delay: float, sampling_rate: float) -> int:
    return int(delay * sampling_rate)


def radians_to_degrees(radians: float) -> float:
    return radians * 180 / math.pi


def degrees_to_radians(degrees: float) -> float:
    return degrees * math.pi / 180
