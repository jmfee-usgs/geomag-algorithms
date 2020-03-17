import numpy as np
from .Ordinate import Ordinate


def calculate_I(measurements, ordinates, metadata):
    # gather average angles for each measurement type
    southdown_angle = average_angle(measurements, "SouthDown")
    northdown_angle = average_angle(measurements, "NorthDown")
    southup_angle = average_angle(measurements, "SouthUp")
    northup_angle = average_angle(measurements, "NorthUp")
    # gather average residuals for each measurement type
    southdown_residual = average_residual(measurements, "SouthDown")
    northdown_residual = average_residual(measurements, "NorthDown")
    southup_residual = average_residual(measurements, "SouthUp")
    northup_residual = average_residual(measurements, "NorthUp")
    # process first inclination angle, assumed to be southdown
    Iprime = southdown_angle
    if Iprime >= 90:
        Iprime -= 180
    Iprime = np.deg2rad(Iprime)
    # gather measurement ordinate averages and ordinate averages by channel
    southdown_ordinate = average_ordinate(ordinates, "SouthDown")
    northdown_ordinate = average_ordinate(ordinates, "NorthDown")
    northup_ordinate = average_ordinate(ordinates, "NorthUp")
    southup_ordinate = average_ordinate(ordinates, "SouthUp")
    # gather ordinates into array
    ordinates = [
        southdown_ordinate,
        northdown_ordinate,
        northup_ordinate,
        southup_ordinate,
    ]

    total_ordinate = average_ordinate(ordinates, None)
    # calculate f for each measurement type
    southdown_f = calculate_f(southdown_ordinate, total_ordinate, Iprime)
    southup_f = calculate_f(southup_ordinate, total_ordinate, Iprime)
    northup_f = calculate_f(northup_ordinate, total_ordinate, Iprime)
    northdown_f = calculate_f(northdown_ordinate, total_ordinate, Iprime)
    # calculate average f that will take the place of f_mean in the next step
    fo = np.average([southdown_f, southup_f, northdown_f, northup_f])
    # get multiplier for hempisphere the observatory is located in
    hs = metadata["hemisphere"]
    # calculate f for every measurement type
    southdown_I = calculate_inclination(
        -180, southdown_angle, 1, southdown_residual, southdown_f, hs
    )
    northup_I = calculate_inclination(
        0, northup_angle, -1, northup_residual, northup_f, hs
    )
    southup_I = calculate_inclination(
        180, southup_angle, -1, southup_residual, southup_f, hs
    )
    northdown_I = calculate_inclination(
        0, northdown_angle, 1, northdown_residual, northdown_f, hs
    )
    # FIXME: Add looping to this method

    inclination = np.average([southdown_I, northup_I, southup_I, northdown_I])

    return inclination, fo, total_ordinate


def calculate_absolutes(f, I, pier_correction):

    i = np.deg2rad(I)
    Fabs = f + pier_correction
    Habs = Fabs * np.cos(i)
    Zabs = Fabs * np.sin(i)

    return Habs, Zabs, Fabs


def calculate_baselines(Habs, Zabs, total_ordinate):
    h_mean = total_ordinate.h
    e_mean = total_ordinate.e
    z_mean = total_ordinate.z

    Hb = np.sqrt(Habs ** 2 - e_mean ** 2) - h_mean
    Zb = Zabs - z_mean

    return Hb, Zb


def calculate_scale(f, measurements, I, pier_correction):
    i = np.deg2rad(I)
    measurements = measurements[-2:]
    angle_diff = (np.diff([m.angle for m in measurements]) / f)[0]
    A = np.cos(i) * angle_diff
    B = np.sin(i) * angle_diff
    delta_f = np.rad2deg(A - B)
    detla_r = abs(np.diff([m.residual for m in measurements]))[0]
    time_delta = np.diff([m.time for m in measurements])[0]
    delta_b = delta_f + (time_delta / 60.0)
    scale_value = f * np.deg2rad(delta_b / detla_r)

    return scale_value


def average_angle(measurements, type):
    if type == "NorthDown":
        # exclude final measurement, which is only used for scaling
        measurements = measurements[type][:-1]
    else:
        measurements = measurements[type]
    return np.average([m.angle for m in measurements])


def average_residual(measurements, type):
    if type == "NorthDown":
        # exclude final measurement, which is only used for scaling
        measurements = measurements[type][:-1]
    else:
        measurements = measurements[type]
    return np.average([m.residual for m in measurements])


def average_ordinate(ordinates, type):
    if type == "NorthDown":
        # exclude final measurement, which is only used for scaling
        ordinates = ordinates[type][:-1]
    elif type is not None:
        ordinates = ordinates[type]
    o = Ordinate(measurement_type=type)
    avgs = np.average([[o.h, o.e, o.z, o.f] for o in ordinates], axis=0)
    o.h, o.e, o.z, o.f = avgs
    return o


def calculate_f(ordinate, total_ordinate, I):
    # get channel means form all ordinates
    h_mean = total_ordinate.h
    e_mean = total_ordinate.e
    z_mean = total_ordinate.z
    f_mean = total_ordinate.f
    # get individual ordinate means
    h = ordinate.h
    e = ordinate.e
    z = ordinate.z
    # calculate f using current step's inclination angle
    f = (
        f_mean
        + (h - h_mean) * np.cos(I)
        + (z - z_mean) * np.sin(I)
        + ((e) ** 2 - (e_mean) ** 2) / (2 * f_mean)
    )
    return f


def calculate_inclination(shift, angle, ud, residual, f, hs):
    return shift + angle + ud * np.rad2deg(hs * np.sin(residual / f))
