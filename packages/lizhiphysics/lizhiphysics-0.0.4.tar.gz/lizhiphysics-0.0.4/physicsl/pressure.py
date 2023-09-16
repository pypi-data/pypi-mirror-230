import math


def pressure_force(f, a):
    """
    计算压强力的函数

    参数:
    F (float): 应用于物体上的力，单位为牛顿 (N)
    A (float): 物体的表面积，单位为平方米 (m^2)

    返回值:
    float: 压强力，单位为帕斯卡 (Pa)
    """
    return f / a


def hydrostatic_pressure(h, g, p0=101325):
    """
    计算静水压力的函数

    参数:
    h (float): 液体的高度，单位为米 (m)
    g (float): 重力加速度，单位为米每平方秒 (m/s^2)
    p0 (float, 可选): 大气压强，单位为帕斯卡 (Pa)。默认值为标准大气压强 (101325 Pa)

    返回值:
    float: 静水压力，单位为帕斯卡 (Pa)
    """
    return p0 + (g * h)


def absolute_pressure(gauge_pressure, p0=101325):
    """
    计算绝对压力的函数

    参数:
    gauge_pressure (float): 弹簧压力计或轮胎压力计等所测得的压力，单位为帕斯卡 (Pa)
    p0 (float, 可选): 大气压强，单位为帕斯卡 (Pa)。默认值为标准大气压强 (101325 Pa)

    返回值:
    float: 绝对压力，单位为帕斯卡 (Pa)
    """
    return gauge_pressure + p0


def ideal_gas_pressure(n, r, t, v):
    """
    计算理想气体压强的函数

    参数:
    n (float): 气体的摩尔数，单位为摩尔 (mol)
    R (float): 气体常数 (8.314 J/(mol·K))
    T (float): 绝对温度，单位为开尔文 (K)
    V (float): 气体的体积，单位为立方米 (m^3)

    返回值:
    float: 理想气体压强，单位为帕斯卡 (Pa)
    """
    return (n * r * t) / v


def kinetic_theory_pressure(n, m, v, v2):
    """
    计算动理论压强的函数

    参数:
    n (float): 分子数，单位为摩尔 (mol)
    m (float): 分子的质量，单位为千克 (kg)
    v (float): 分子的平均速度，单位为米每秒 (m/s)
    v2 (float): 气体的体积，单位为立方米 (m^3)

    返回值:
    float: 动理论压强，单位为帕斯卡 (Pa)
    """
    return (n * m * v ** 2) / (3 * v2)


def bernoulli_pressure(p0, v0, h, g=9.8):
    """
    计算伯努利压强的函数

    参数:
    p0 (float): 流体的初始压强，单位为帕斯卡 (Pa)
    v0 (float): 流体的初始速度，单位为米每秒 (m/s)
    h (float): 流体的高度，单位为米 (m)
    g (float, 可选): 重力加速度，单位为米每平方秒 (m/s^2)。默认值为地球表面重力加速度 (9.8 m/s^2)

    返回值:
    float: 伯努利压强，单位为帕斯卡 (Pa)
    """
    return p0 + (0.5 * (v0 ** 2) * (1 - (h * g)))


def pressure_conversion(p, unit):
    """
    压强单位转换函数

    参数:
    p (float): 压强值
    unit (str): 目标单位，可选为 "Pa"、"atm"、"mmHg" 或 "psi"

    返回值:
    float: 转换后的压强值
    """
    if unit == "Pa":
        return p
    elif unit == "atm":
        return p / 101325
    elif unit == "mmHg":
        return p / 133.322
    elif unit == "psi":
        return p / 6894.76
    else:
        raise ValueError("无效的压强单位参数！")


def fluid_column_pressure(h, rho, g):
    """
    计算液体柱的压强的函数

    参数:
    h (float): 液体柱的高度，单位为米 (m)
    rho (float): 液体的密度，单位为千克每立方米 (kg/m^3)
    g (float): 重力加速度，单位为米每平方秒 (m/s^2)

    返回值:
    float: 液体柱的压强，单位为帕斯卡 (Pa)
    """
    return rho * g * h


def pressure_drop(q, a, rho, v):
    """
    计算压力降的函数

    参数:
    q (float): 流体的流量，单位为立方米每秒 (m^3/s)
    A (float): 流体的流通截面积，单位为平方米 (m^2)
    rho (float): 流体的密度，单位为千克每立方米 (kg/m^3)
    v (float): 流体的速度，单位为米每秒 (m/s)

    返回值:
    float: 压力降，单位为帕斯卡 (Pa)
    """
    return (rho * (v**2)) / 2 - (q / a)


def hydrodynamic_pressure(rho, v):
    """
    计算流体运动的动压的函数

    参数:
    rho (float): 流体的密度，单位为千克每立方米 (kg/m^3)
    v (float): 流体的速度，单位为米每秒 (m/s)

    返回值:
    float: 动压，单位为帕斯卡 (Pa)
    """
    return (rho * (v**2)) / 2


def airspeed_velocity(p, rho):
    """
    计算风速的函数

    参数:
    p (float): 空气的静压，单位为帕斯卡 (Pa)
    rho (float): 空气的密度，单位为千克每立方米 (kg/m^3)

    返回值:
    float: 风速，单位为米每秒 (m/s)
    """
    return math.sqrt((2 * p) / rho)


def osmotic_pressure(m, r, t):
    """
    计算渗透压的函数

    参数:
    M (float): 溶质的摩尔浓度，单位为摩尔每升 (mol/L)
    R (float): 气体常数，单位为卡路里/(摩尔·开尔文) (cal/(mol·K))
    T (float): 绝对温度，单位为开尔文 (K)

    返回值:
    float: 渗透压，单位为帕斯卡 (Pa)
    """
    return m * 1000 * r * t


def capillary_pressure(sigma, theta, r):
    """
    计算毛细管压强的函数

    参数:
    sigma (float): 表面张力，单位为牛顿每米 (N/m)
    theta (float): 液体与毛细管壁之间的接触角，单位为弧度 (rad)
    r (float): 毛细管的半径，单位为米 (m)

    返回值:
    float: 毛细管压强，单位为帕斯卡 (Pa)
    """
    return (2 * sigma * math.cos(theta)) / r


def magnetic_pressure(b):
    """
    计算磁场的磁压的函数

    参数:
    B (float): 磁场的磁感应强度，单位为特斯拉 (T)

    返回值:
    float: 磁场的磁压，单位为帕斯卡 (Pa)
    """
    return (b**2) / (2 * 8.85E-12)


def radiation_pressure(i, c):
    """
    计算辐射的辐压的函数

    参数:
    I (float): 辐射的辐射通量，单位为瓦特每平方米 (W/m^2)
    c (float): 光速，单位为米每秒 (m/s)

    返回值:
    float: 辐射的辐压，单位为帕斯卡 (Pa)
    """
    return i / c


def sound_pressure_level(p, p0):
    """
    计算声压级的函数

    参数:
    p (float): 实际声压，单位为帕斯卡 (Pa)
    p0 (float): 参考声压，单位为20微帕斯卡 (20 µPa)

    返回值:
    float: 声压级，单位为分贝 (dB)
    """
    return 20 * math.log10(p / p0)


def wind_chill_temperature(t, v):
    """
    计算风寒温度的函数

    参数:
    T (float): 空气温度，单位为摄氏度 (°C)
    V (float): 风速，单位为米每秒 (m/s)

    返回值:
    float: 风寒温度，单位为摄氏度 (°C)
    """
    wct = 13.12 + 0.6215 * t - 11.37 * (v**0.16) + 0.3965 * t * (v**0.16)
    return wct


def acoustic_impedance(rho, c):
    """
    计算声阻抗的函数

    参数:
    rho (float): 流体的密度，单位为千克每立方米 (kg/m^3)
    c (float): 声速，单位为米每秒 (m/s)

    返回值:
    float: 声阻抗，单位为牛顿秒每立方米 (Ns/m^3)
    """
    return rho * c


def laplace_pressure(sigma, r):
    """
    计算拉普拉斯压强的函数

    参数:
    sigma (float): 表面张力，单位为牛顿每米 (N/m)
    r (float): 液滴的半径，单位为米 (m)

    返回值:
    float: 拉普拉斯压强，单位为帕斯卡 (Pa)
    """
    return 2 * sigma / r


def yield_pressure(y, t):
    """
    计算材料的屈服压力的函数

    参数:
    Y (float): 材料的屈服强度，单位为帕斯卡 (Pa)
    t (float): 材料的厚度，单位为米 (m)

    返回值:
    float: 材料的屈服压力，单位为帕斯卡 (Pa)
    """
    return y / (2 * t)


def interfacial_tension(w, l1):
    """
    计算界面张力的函数

    参数:
    W (float): 界面的总能量，单位为焦耳 (J)
    L (float): 界面的长度，单位为米 (m)

    返回值:
    float: 界面张力，单位为牛顿每米 (N/m)
    """
    return w / l1


def streamer_discharge_pressure(i, b, d):
    """
    计算电流放电流出的压力的函数

    参数:
    I (float): 放电电流，单位为安培 (A)
    B (float): 磁场强度，单位为特斯拉 (T)
    d (float): 放电间隙，单位为米 (m)

    返回值:
    float: 电流放电产生的压力，单位为帕斯卡 (Pa)
    """
    return 0.098 * i**2 * b**2 / d**4


def osmotic_pressure_van_hoff(i, m, r, t):
    """
    计算渗透压的函数（van 't Hoff公式）

    参数:
    i (int): 溶质的完全离解度
    M (float): 溶质的摩尔浓度，单位为摩尔每升 (mol/L)
    R (float): 气体常数，单位为卡路里/(摩尔·开尔文) (cal/(mol·K))
    T (float): 绝对温度，单位为开尔文 (K)

    返回值:
    float: 渗透压，单位为帕斯卡 (Pa)
    """
    return i * m * 1000 * r * t


def overpressure(p, pc):
    """
    计算超压的函数

    参数:
    P (float): 爆炸所产生的压力，单位为帕斯卡 (Pa)
    Pc (float): 环境所能承受的最大压力，单位为帕斯卡 (Pa)

    返回值:
    float: 超压，单位为帕斯卡 (Pa)
    """
    return p - pc


def suction_pressure(pa, pb):
    """
    计算吸管的吸力的函数

    参数:
    Pa (float): 大气压力，单位为帕斯卡 (Pa)
    Pb (float): 吸口处的绝对压力，单位为帕斯卡 (Pa)

    返回值:
    float: 吸管的吸力，单位为帕斯卡 (Pa)
    """
    return pa - pb


def constant_force_pressure(f, a):
    """
    计算固定作用力的压强的函数

    参数:
    F (float): 固定作用力，单位为牛顿 (N)
    A (float): 受力面积，单位为平方米 (m^2)

    返回值:
    float: 压强，单位为帕斯卡 (Pa)
    """
    return f / a
