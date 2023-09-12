import numpy as np


def solid_angle(half_angle_rad):
    """
    Returns cone's solid_angle in sr.
    """
    cap_hight = 1.0 - np.cos(half_angle_rad)
    return 2.0 * np.pi * cap_hight


def half_angle(solid_angle_sr):
    """
    Returns cone's half-angle in rad.
    """
    cap_hight = solid_angle_sr / (2.0 * np.pi)
    return np.arccos(-cap_hight + 1.0)


def half_angle_space(stop_half_angle_rad, num):
    assert num >= 1
    assert stop_half_angle_rad > 0.0

    cone_stop_sr = solid_angle(stop_half_angle_rad)
    cone_step_sr = cone_stop_sr / num

    edges = [0]
    for i in np.arange(1, num):
        a = half_angle(i * cone_step_sr)
        edges.append(a)
    edges.append(stop_half_angle_rad)
    return np.array(edges)
