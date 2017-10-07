__author__ = 'roehrig'

import math

from warsa.energy import solar_radiation


def atmospheric_pressure(z):
    """ Calculates the atmospheric pressure in kpa as a function of the elevation above the sea level.

    The atmospheric pressure, P, is the pressure exerted by the weight of the earth's atmosphere. Evaporation at high
    altitudes is promoted due to low atmospheric pressure as expressed in the psychrometric constant. The effect is,
    however, small and in the calculation procedures, the average value for a LOCATION is sufficient. A simplification
    of the ideal gas law, assuming 20 C for a standard atmosphere, can be employed to calculate P (FAO56)

    :param z: elevation above sea level [m]
    :return: atmospheric pressure [kPa]
    """
    return 101.3*((293.0-0.00652*z)/293.0)**5.26


def psychrometric_constant(p, a_psy=0.000665):
    """
    :param p: atmospheric pressure [kPa]
    :param a_psy: coefficient depending on the type of the ventilation of the bulb [1/C]
        Examples:
        a_psy = 0.000665 (default)
        a_psy = 0.000662 for ventilated (Asmann type) psychrometers, with an air movement of some 5 m/s
        a_psy = 0.000800 for natural ventilated psychrometers (about 1 m/s)
        a_psy = 0.001200 for non-ventilated psychrometers installed indoors
    :return: psychrometric constant[]
    """
    return a_psy * p


def saturation_vapour_pressure(t):
    """
    :param t: temperature [C]
    :return: saturation vapour pressure
    """
    return 0.6108 * math.exp((17.27 * t)/(t + 237.3))


def slope_of_saturation_vapour_pressure_curve(t):
    """
    
    :param t:
    :type t:
    :return:
    :rtype:
    """
    """
    page 37
    Inputs
        tmax :  maximum air temperature [C]
        tmin :  minimum air temperature [C]
    """
    return (4098.0 * saturation_vapour_pressure(t)) / (t + 237.3)**2


def actual_vapour_pressure(**args):
    """
    page 37 , 38 , 39

    :param args:
        tmax :  maximum air temperature [C]
        tmin :  minimum air temperature [C]
        tdew :  dewpoint temperature [C]
        twet :  wet bulb temperature temperature [C]
        tdry :  dry bulb temperature temperature [C]
        apsy :  coefficient depending on the type of ventilation of the wet bulb
        rhmax : maximum relative humidity [%]
        rhmin : minimum relative humidity [%]
        rhmean : mean relative humidity [%]
        z : elevation above sea level [m]
    :type args: float
    :return:
    :rtype:
    """
    if 'tdew' in args:
        tdew = args['tdew']
        return 0.6108 * math.exp((17.27 * tdew)/(tdew + 237.3))
    elif 'twet' in args and 'tdry' in args and 'psyc' in args:
            twet = args['twet']
            return saturation_vapour_pressure(twet) - args['psyc'] * (args['tdry'] - twet)
    elif 'rh' in args and 'type' in args:
        return 0.01 * args['rh'] * saturation_vapour_pressure(args['type'])
    elif 'rh' in args and 'tmin' in args and 'tmax' in args:
        return 0.01 * args['rh'] * (saturation_vapour_pressure(args['tmin'])+saturation_vapour_pressure(args['tmax'])) / 2.0
    elif 'rhmin' in args and 'rhmax' in args and 'tmin' in args and 'tmax' in args:
        return 0.01 * (args['rhmin'] * saturation_vapour_pressure(args['tmax']) + args['rhmax'] * saturation_vapour_pressure(args['tmin'])) / 2.0


def reference_evapotranspiration(lat, z, albedo, day, n, u2, g=0.0, tmin=None, tmax=None, t=None, rhmin=None, rhmax=None, rh=None):
    """

    :param lat:
    :type lat:
    :param z:
    :type z:
    :param albedo:
    :type albedo:
    :param day:
    :type day:
    :param n:
    :type n:
    :param u2:
    :type u2:
    :param g:
    :type g:
    :param tmin:
    :type tmin:
    :param tmax:
    :type tmax:
    :param t:
    :type t:
    :param rhmin:
    :type rhmin:
    :param rhmax:
    :type rhmax:
    :param rh:
    :type rh:
    :return:
    :rtype:
    """
    """
    page 65
    Args:
        Rn : net radiation at the crop surface [MJ m-2 day-1]
        G : soil heat flux density [MJ m-2 day-1]
        T : air temperature at 2 m height [C]
        u2 : wind speed at 2 m height [m s-1]
        es : saturation vapour pressure [kPa]
        ea : actual vapour pressure [kPa]
        dalta : slope vapour pressure curve [kPa C-1]
        gama : psychrometric constant [kPa C-1]
        tmin (float): a) minimum daily temperature or b) mean temperature if maximum temperature is None
        tmax (float): a) maximum daily temperature or b) None if mean temperature was given
        rhmin
        rhmax
    """

    patm = atmospheric_pressure(z)
    psyc = psychrometric_constant(patm)

    ea, rn, sl, es = None, None, None, None
    if t is not None:
        if rh:
            ea = actual_vapour_pressure(rh=rh, t=t)
        elif rhmin and rhmax:
            ea = actual_vapour_pressure(rhmin=rhmin, rhmax=rhmax, tmin=t, tmax=t)
        rn = solar_radiation.net_radiation_daily(lat, t, t, albedo, n, ea, day)
        sl = slope_of_saturation_vapour_pressure_curve(t)
        es = saturation_vapour_pressure(t)
        vfac = psyc * 900 * u2 * (es-ea) / (t + 273.14)
    elif tmin is not None and tmax is not None:
        if rh:
            ea = actual_vapour_pressure(rh=rh, tmin=tmin, tmax=tmax)
        elif rhmin and rhmax:
            ea = actual_vapour_pressure(rhmin=rhmin, rhmax=rhmax, tmin=tmin, tmax=tmax)
        rn = solar_radiation.net_radiation_daily(lat, tmin, tmax, albedo, n, ea, day)
        tmean = (tmin + tmax) / 2.0
        sl = slope_of_saturation_vapour_pressure_curve(tmean)
        es = (saturation_vapour_pressure(tmin) + saturation_vapour_pressure(tmax)) / 2.0
        vfac = psyc * 900 * u2 * (es-ea) / (tmean + 273.14)
    return (0.408 * sl *(rn-g) + vfac) / (sl + (psyc * (1.0 + (0.34 * u2))))


