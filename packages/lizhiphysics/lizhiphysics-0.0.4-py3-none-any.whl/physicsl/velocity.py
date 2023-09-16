import math
import sympy as sp


def velocity(dis, t):
    if not isinstance(dis, (int, float)) or not isinstance(t, (int, float)):
        raise TypeError("distance and time must be numbers")
    if dis <= 0 or t <= 0:
        raise ValueError("distance and time can't be <= 0")
    else:
        a = dis / t
        return a


def distance(vel, t):
    if not isinstance(vel, (int, float)) or not isinstance(t, (int, float)):
        raise TypeError("velocity and time must be numbers")
    if vel <= 0 or t <= 0:
        raise ValueError("velocity and time can't be <= 0")
    else:
        a = vel * t
        return a


def time(vel, dis):
    if not isinstance(vel, (int, float)) or not isinstance(dis, (int, float)):
        raise TypeError("distance and velocity must be numbers")
    if vel <= 0 or dis <= 0:
        raise ValueError("distance and velocity can't be <= 0")
    else:
        a = dis / vel
        return a


def free_fall_speed(high, g=9.8):
    if not isinstance(high, (int, float)) or not isinstance(g, (int, float)):
        raise TypeError("distance and velocity must be numbers")
    if high <= 0 or g <= 0:
        raise ValueError("distance and velocity can't be <= 0")
    else:
        v = math.sqrt(2 * g * high)
        return v


def instantaneous_velocity(delta_s, delta_t):
    if not isinstance(delta_s, (int, float)) or not isinstance(delta_t, (int, float)):
        raise TypeError(" delta_t and delta_s must be numbers")
    if delta_s <= 0 or delta_t <= 0:
        raise ValueError(" delta_t and delta_s can't be <= 0")
    else:
        t = sp.symbols('t')
        s = delta_s / delta_t
        v = sp.limit(s, t, 0)
        return v


def uniform_linear_motion(s, t):
    if not isinstance(s, (int, float)) or not isinstance(t, (int, float)):
        raise TypeError("s and t must be numbers")
    if t <= 0:
        raise ValueError("t can't be zero")

    return s / t


def acceleration(v_f, v_i, t):
    if not isinstance(v_f, (int, float)) or not isinstance(v_i, (int, float)) or not isinstance(t, (int, float)):
        raise TypeError("v_f, v_i, and t must be numbers")
    if t <= 0:
        raise ValueError("t can't be zero")

    return (v_f - v_i) / t


def uniformly_accelerated_motion_initial_velocity(v_i, a, t):
    if not isinstance(v_i, (int, float)) or not isinstance(a, (int, float)) or not isinstance(t, (int, float)):
        raise TypeError("v_i, a, and t must be numbers")
    return v_i + a * t


def uniformly_accelerated_motion_displacement(v_i, a, t):
    if not isinstance(v_i, (int, float)) or not isinstance(a, (int, float)) or not isinstance(t, (int, float)):
        raise TypeError("v_i, a, and t must be numbers")
    return v_i * t + 0.5 * a * t**2


def displacement(v_i, v_f, t):
    if not isinstance(v_i, (int, float)) or not isinstance(v_f, (int, float)) or not isinstance(t, (int, float)):
        raise TypeError("v_i, v_f, and t must be numbers")
    return 0.5 * (v_i + v_f) * t


def newtons_second_law(mass, acc):
    if not isinstance(mass, (int, float)) or not isinstance(acc, (int, float)):
        raise TypeError("mass and acceleration must be numbers")
    return mass * acc


def kinetic_energy(mass, vel):
    if not isinstance(mass, (int, float)) or not isinstance(vel, (int, float)):
        raise TypeError("mass and velocity must be numbers")
    return 0.5 * mass * vel**2


def potential_energy(mass, height, gravity=9.81):
    if not isinstance(mass, (int, float)) or not isinstance(height, (int, float)):
        raise TypeError("mass, height, and gravity must be numbers")
    if not isinstance(gravity, (int, float)):
        raise TypeError("mass, height, and gravity must be numbers")
    return mass * gravity * height


def momentum(mass, vel):
    if not isinstance(mass, (int, float)) or not isinstance(velocity, (int, float)):
        raise TypeError("mass and velocity must be numbers")
    return mass * vel


def impulse(force, t):
    if not isinstance(force, (int, float)) or not isinstance(t, (int, float)):
        raise TypeError("force and time must be numbers")
    return force * t


def rebound_velocity(e, initial_velocity):
    if not isinstance(e, (int, float)) or not isinstance(initial_velocity, (int, float)):
        raise TypeError("e and initial_velocity must be numbers")
    return -e * initial_velocity


def rebound_velocity_with_restitution(e, in_vel, reb_vel):
    if not isinstance(e, (int, float)) or not isinstance(in_vel, (int, float)) or not isinstance(reb_vel, (int, float)):
        raise TypeError("e, initial_velocity, and rebound_velocity must be numbers")
    return -e * (in_vel - reb_vel)


def resultant_velocity(v_x, v_y, v_z):
    if not isinstance(v_x, (int, float)) or not isinstance(v_y, (int, float)) or not isinstance(v_z, (int, float)):
        raise TypeError("v_x, v_y, and v_z must be numbers")
    return math.sqrt(v_x**2 + v_y**2 + v_z**2)


def linear_velocity(radius, angular_velocity):
    return radius * angular_velocity


def centripetal_acceleration(radius, linear_vel):
    return (linear_vel ** 2) / radius


def centripetal_force(mass, centripetal_acc):
    return mass * centripetal_acc


def gravitational_force(m1, m2, dis, g=6.67e-11):
    return g * m1 * m2 / (dis ** 2)


def work_kinetic_energy_principle(kinetic_energy_final, kinetic_energy_initial):
    return kinetic_energy_final - kinetic_energy_initial


def speed_of_sound(temperature):
    return 331.3 * (1 + temperature / 273.15) ** 0.5


def bandwidth(data_size, transfer_time):
    return data_size / transfer_time
