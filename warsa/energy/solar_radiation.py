__author__ = 'roehrig'

from math import sin, cos, acos, tan, sqrt, exp


def extraterrestrial_radiation_daily(dr, ws, lat, sd):
    """
    :param dr: inverse relative distance Earth-Sun
    :param ws: sunset hour angle [rad]
    :param lat: latitude [rad]
    :param sd: solar declination [rad]
    :return: daily extraterrestrial radiation []
    """
    # solar_constant = 0.0820 # MJ.m-2.min-1
    # (24.0 * 60.0 / pi) * solar_constant = 37.586031360582005
    return 37.586031360582005 * dr * (ws * sin(lat) * sin(sd) + cos(lat) * cos(sd) * sin(ws))


def extraterrestrial_radiation_hourly(dr, ws1, ws2, lat, sd):
    """
    :param dr: inverse relative distance Earth-Sun
    :param ws1: solar time angle at beginning of period [rad]
    :param ws2: solar time angle at end of period [rad]
    :param lat: latitude [rad]
    :param sd: solar declination [rad]
    :return: hourly extraterrestrial radiation []
    """
    # solar_constant = 0.0820 # MJ.m-2.min-1
    # (12.0 * 60.0 / pi) * solar_constant = 18.793015680291003
    return 18.793015680291003 * dr * ((ws2 - ws1) * sin(lat) * sin(sd) + cos(lat) * cos(sd) * (sin(ws2) - sin(ws1)))


# def solar_time_angles(ws):
#     '''
#     TODO
#     '''
#     pass


def inverse_relative_distance_earth_sun(day):
    """
    :param day: day of the year (1 to 365)
    :return: inverse relative distance Earth-Sun []
    """
    # 2.0 * pi / 365 = 0.01721420632103996
    return 1 + 0.033 * cos(0.01721420632103996 * day)


def solar_declination(day):
    """

    :param day: day of the year (1 to 365)
    :return: solar declination []
    """
    # 2.0 * pi / 365 = 0.01721420632103996
    return 0.409 * sin(0.01721420632103996 * day - 1.39)


def sunset_hour_angle(lat, sd):
    """
    :param lat: latitude [rad]
    :param sd: solar declination [rad]
    :return: sunset hour angle [rad]
    """
    return acos(-tan(lat) * tan(sd))


def daylight_hours(ws):
    """
    :param ws: sunset hour angle [rad]
    :return: daylight hours [hour]
    """
    # 24.0 / pi = 7.639437268410976
    return 7.639437268410976 * ws


def shortwave_radiation_daily(r0, nt, n=None, a=0.25, b=0.50):
    """ If n is None, returns the shortwave radiation for a cloudless day (n==nt)
    :param r0: extraterrestrial radiation [MJ m-2 day-1]
    :param n: actual duration of sunshine (cloudless hours) [hour]
    :param nt: maximum possible duration of sunshine or daylight hours [hour]
    :param a: regression constant, expressing the fraction of extraterrestrial radiation reaching the earth on overcast days (n = 0)
    :param a + b: fraction of extraterrestrial radiation reaching the earth on clear days (n = nt)
    :return: daily total shortwave radiation reaching the earth [MJ m-2 day-1]
    """
    return (a + b * n / nt) * r0 if n else (a + b) * r0


def net_shortwave_radiation_daily(rs, albedo):
    """
    :param rs: daily shortwave radiation [MJ m-2 day-1]
    :param albedo: reflection coefficient (0 <= albedo <= 1), which is 0.23 for the hypothetical grass reference crop [-]
    :return: daily net shortwave radiation reaching the earth [MJ m-2 day-1]
    """
    return (1.0 - albedo) * rs


def net_longwave_radiation_daily(t_min, t_max, rs, rs0, ea=None, ac=1.35, bc=0.35):
    """
    :param t_min: minimum temperature during the 24-hour period [C]
    :param t_max: maximum temperature during the 24-hour period [C]
    :param rs: measured or calculated shortwave radiation [MJ m-2 day-1]
    :param rs0: calculated clear-sky shortwave radiation [MJ m-2 day-1]
    :param ea: actual vapour pressure [kPa]
    :param ac:
    :param bc:
    :return: daily net longwave radiation
    """
    t_min_k = t_min + 273.15
    t_max_k = t_max + 273.15
    if ea:
        return 4.903e-9 * (t_min_k**4 + t_max_k**4) * 0.5 * (0.34 - 0.14 * sqrt(ea)) * (ac * rs / rs0 - bc)
    else:
        t_mean = (t_min + t_max) / 2.0
        return 4.903e-9 * (t_min_k**4 + t_max_k**4) * 0.5 * (-0.02 + 0.261 * exp(-7.77e10**-4 * t_mean**2)) * (ac * rs / rs0 - bc)


def net_radiation_daily(lat, t_min, t_max, albedo, day, n=None, ea=None):
    """
    :param lat: latitude [rad]
    :param t_min: minimum temperature during the 24-hour period [C]
    :param t_max: maximum temperature during the 24-hour period [C]
    :param albedo: reflection coefficient (0 <= albedo <= 1), which is 0.23 for the hypothetical grass reference crop [-]
    :param day: day of the year (1 to 365)
    :param n: actual duration of sunshine (cloudless hours) [hour]
    :param ea: actual vapour pressure [kPa]
    :return: daily net radiation
    """
    dr = inverse_relative_distance_earth_sun(day)
    sd = solar_declination(day)
    ws = sunset_hour_angle(lat, sd)
    nt = daylight_hours(ws)
    r0 = extraterrestrial_radiation_daily(dr, ws, lat, sd)
    rs = shortwave_radiation_daily(r0, n, nt)
    rs0 = shortwave_radiation_daily(r0, nt, nt)
    rns = net_shortwave_radiation_daily(rs, albedo)
    rnl = net_longwave_radiation_daily(t_min, t_max, rs, rs0, ea)
    return rns - rnl


