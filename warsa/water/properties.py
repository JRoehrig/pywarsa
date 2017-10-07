# -- coding: utf-8
# See also:
# http://www.imr.no/~bjorn/python/seawater/
# http://www.code10.info/index.php?option=com_content&view=category&id=54&Itemid=79

import re
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def pure_water_density(t):
    return pure_water_density_tanaka(t)


def pure_water_density_tanaka(t, a5=0.999974950):
    """Equation according Tanaka, M., et. al; Recommended table for the density of water between 0 C and 40 C based on
    recent experimental reports, Metrologia, 2001, 38, 301-309

    :param t: water temperature (°C)
    :param a5: density of SMOW water under one atmosphere at temperature type. a5 must be changed if other water used (e.g., tap water).
    :return: water density at temperature type in mg/l
    """
    a1 = -3.983035  # deg C
    a2 = 301.797  # deg C
    a3 = 522528.9  # (deg C)**2
    a4 = 69.34881  # deg C
    return 1000.0 * (a5 * (1.0 - ((t + a2)*(t + a1)*(t + a1)) / (a3 * (t + a4))))


def pure_water_density_craig(t):
    # Eq. 14 in Fofonoff, P. and R. C. Millard Jr (1983): Algorithms for computation of fundamental properties of
    # seawater. According to Craig (1961)
    a0 = 999.842594
    a1 = 6.793952E-2
    a2 = -9.095290E-3
    a3 = 1.001685E-4
    a4 = -1.120083E-6
    a5 = 6.536332E-9
    return a0 + (a1 + (a2 + (a3 + (a4 + (a5 * t)) * t) * t) * t) * t


def water_density_zero_pressure(s, t):
    # Eq. 13 in Fofonoff, P. and R. C. Millard Jr (1983): Algorithms for computation of fundamental properties of
    # seawater. According to Craig (1961)
    b0 = 8.24493E-1
    b1 = -4.0899E-3
    b2 = 7.6438E-5
    b3 = -8.2467E-7
    b4 = 5.3875E-9
    c0 = -5.72466E-3
    c1 = 1.0227E-4
    c2 = -1.6546E-6
    d0 = 4.8314E-4
    # d = pure_water_density_craig(type)
    d = pure_water_density(t)
    return d + (b0 + (b1 + (b2 + (b3 + b4 * t) * t) * t) * t) * s + \
           (c0 + (c1 + (c2 * t)) * t) * (s ** 1.5) + d0 * s * s


def pure_water_secant_bulk_modulus(t):
    e0 = 19652.21
    e1 = 148.4206
    e2 = -2.327105
    e3 = 1.360477E-2
    e4 = -5.155288E-5
    return e0 + (e1 + (e2 + (e3 + e4 * t) * t) * t) * t


def secant_bulk_modulus(s, t, p):
    """Secant bulk modulus according to Fofonoff, P. and R. C. Millard Jr (1983): Algorithms for computation of
    fundamental properties of seawater. Equation 15
    :param s:
    :param t:
    :param p:
    :return:
    """
    k0 = 8.50935E-5
    k1 = -6.12293E-6
    k2 = 5.2787E-8
    bw = k0 + (k1 + (k2 * t)) * t

    h0 = 3.239908
    h1 = 1.43713E-3
    h2 = 1.16092E-4
    h3 = -5.77905E-7
    aw = h0 + (h1 + (h2 + h3 * t) * t) * t

    e0 = 19652.21
    e1 = 148.4206
    e2 = -2.327105
    e3 = 1.360477E-2
    e4 = -5.155288E-5
    kw = e0 + (e1 + (e2 + (e3 + e4 * t ) * t ) * t ) * t  # eq. 19

    m0 = -9.9348E-7
    m1 = 2.0816E-8
    m2 = 9.1697E-10
    b = bw + (m0 + m1 * t + m2 * t * t) * s  # eq. 18

    i0 = 2.2838E-3
    i1 = -1.0981E-5
    i2 = -1.6078E-6
    j0 = 1.91075E-4
    a = aw + (i0 + i1 * t + i2 * t * t) * s + j0 * (s ** 1.5)  # eq. 17

    f0 = 54.6746
    f1 = -0.603459
    f2 = 1.09987E-2
    f3 = -6.1670E-5
    g0 = 7.944E-2
    g1 = 1.6483E-2
    g2 = -5.3009E-4
    k0 = kw + (f0 + (f1 + (f2 + (f3 * t) * t) * t) * t) * s + (g0 + g1 * t + g2 * t * t) * (s ** 1.5)  # eq. 16

    return k0 + (a + b * p) * p  # eq. 15


def water_density(t=20.0, s=0.0, p=0.0):
    # Eq. 7 in Fofonoff, P. and R. C. Millard Jr (1983): Algorithms for computation of fundamental properties of
    # seawater
    if p == 0.0:
        if s == 0.0:
            return pure_water_density(t)
        else:
            return water_density_zero_pressure(s, t)
    else:
        p *= 1.0E-5
        return water_density_zero_pressure(s, t) / (1.0 - p/secant_bulk_modulus(s, t, p))


def conductivity_to_salinity(cond, t, p):
    """
    :param cond: conductivity Sm-1
    :param t: temperature °C
    :param p: decibar
    :return: salinity (PSS-78)
    """
    cond /= 4.2914  # transform into relative conductivity  (cond(35, 15, 0) = 4.2914 Sm-1;  cond = 1.0 for s = 35.0)

    c0 = 0.6766097
    c1 = 2.00564E-2
    c2 = 1.104259E-4
    c3 = -6.9698E-7
    c4 = 1.0031E-9
    rt_35 = c0 + (c1 + (c2 + (c3 + c4 * t) * t) * t) * t  # eq. 3 for salinity 35
    
    e1 = 2.070E-5
    e2 = -6.370E-10
    e3 = 3.989E-15
    d1 = 3.426E-2
    d2 = 4.464E-4
    d3 = 4.215E-1
    d4 = -3.107E-3
    rp = 1.0 + ((e1 + (e2 + e3 * p) * p) * p) / (1.0 + (d1 + d2 * p * t) * p * t + (d3 + d4 * t) * cond)  # eq. 4

    rt = cond / (rt_35 * rp)  # eq. page 8 below
    rt = math.sqrt(math.fabs(rt))  # change rt**0.5, rt**1.5, rt**1.5, etc.

    a0 = 0.0080
    a1 = -0.1692
    a2 = 25.3851
    a3 = 14.0941
    a4 = -7.0261
    a5 = 2.7081
    
    b0 = 0.0005
    b1 = -0.0056
    b2 = -0.0066
    b3 = -0.0375
    b4 = 0.0636
    b5 = -0.0144
    
    k = 0.0162

    dt = t - 15
    ds = (dt / (1 + k * dt)) * (b0 + (b1 + (b2 + (b3 + (b4 + b5 * rt) * rt) * rt) * rt) * rt)  # eq. 2

    return a0 + (a1 + (a2 + (a3 + (a4 + a5 * rt) * rt) * rt) * rt) * rt + ds  # eq. 1


def water_saturation_vapour_pressure(t):
    return water_saturation_vapour_pressure_cimo(t)


def water_saturation_vapour_pressure_wmo(t):
    """Returns the water vapour pressure according to World Meteorological Organization, Technical Regulations,
    Basic Documents No. 2, Volume I - General meteorological standards and recommended practices, Appendix A,
    WMO-No. 49, Geneva 2011, updated 2012.
    :param t: water temperature (°C)
    :return: water vapour pressure in Pascal (Pa)
    """
    t += 273.15
    return 100.0 * 10.0**(10.79574 * (1-273.16/t) - 5.02800 * math.log10(t/273.16) +
                          1.50475E-4 * (1 - 10**(-8.2969 * (t/273.16-1))) +
                          0.42873E-3 * (10**( 4.76955 * (1 - 273.16/t)) - 1) + 0.78614)


def water_saturation_vapour_pressure_cimo(t):
    """Returns the water vapour pressure according to World Meteorological Organization, Guide to Meteorological
    Instruments and Methods of Observation, Appendix 4B, WMO-No. 8 (CIMO Guide), Geneva 2008.
    :param t: water temperature (°C)
    :return: water vapour pressure in Pascal (Pa)
    """
    return 611.2 * math.exp((17.62 * t/(243.12 + t)))


def water_saturation_vapour_pressure_iapws(t):
    """Returns the water vapour pressure according to W. Wagner and A. Pruss (1992) J. Phys. Chem. Reference Data, 22,
    783–787.
    See http://www.kayelaby.npl.co.uk/chemistry/3_4/3_4_2.html
    Valid only above the triple point. The IAWPS formulation 1995 (Wagner and Pruß, 2002) is valid in the temperature
    range 273.16 K < T < 647.096 K. See http://cires1.colorado.edu/~voemel/vp.html
    :param t: water temperature (°C)
    :return: water vapour pressure in Pascal (Pa)
    """
    tc = 647.096  # K
    pc = 22064000   # Pa
    a1 = -7.85951783
    a2 = 1.84408259
    a3 = -11.7866497
    a4 = 22.6807411
    a5 = -15.9618719
    a6 = 1.80122502
    t += 273.15
    tau = 1 - t/tc
    return pc * math.exp((a1 * tau + a2 * tau**1.5 + a3 * tau**3 + a4 * tau**3.5 + a5 * tau**4 + a6 * tau**7.5) * tc / t)


def water_saturation_vapour_pressure_table(t=None, columns=3, latex=False):

    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i+n]
    if not t:
        t = range(0, 101, 5)
        df = pd.DataFrame()
    for i, t0 in enumerate(chunks(t, len(t)/columns)):
        t1, vp1 = zip(*[(t1, 0.001 * water_saturation_vapour_pressure(t1)) for t1 in t0])
        df1 = pd.DataFrame({'T' + str(i): t1, 'VP'+str(i): vp1})
        df1['VP'+str(i)] = df1['VP'+str(i)].map('{:.4f}'.format)
        df = pd.concat([df,df1], axis=1)
    if latex:
        dfl = df.to_latex(index=False)
        dfl = re.sub(r"T\d{1}", "T (\degree C)", dfl)
        dfl = re.sub(r"VP\d{1}", "P (kPa)", dfl)
        dfl = re.sub(r"NaN", "", dfl)
        print dfl
    return df


def water_viscosiity():
    pass


def plot_conductivity_to_salinity():
    for t in np.arange(0.0, 35.0, 5.0):
        c0, s0 = zip(*[(cond, conductivity_to_salinity(cond, t, 0.0)) for cond in np.arange(0, 6.0, 0.1)])
        plt.plot(c0, s0, label='T=' + str(t) + u'°C')

    plt.title('Water salinity')
    plt.ylabel('Water salinity (PSS-78)')
    plt.xlabel(u'Water conductivity (S/m)')
    plt.legend(loc='lower right', prop={'size': 8})
    plt.ylim(ymin=0.0)
    plt.grid(True)
    plt.show()


def plot_pure_water_density():
    t, d = zip(*[(t, pure_water_density(t)) for t in range(0, 41)])
    plt.plot(t, d)
    plt.title('Water density')
    plt.ylabel('Water density in mg/l')
    plt.xlabel(u'Water temperature in °C')
    plt.ylim(990.0, 1000.1)
    plt.grid(True)
    plt.show()


def plot_water_density_comparison():
    t_tnk, d_tnk = zip(*[(t, pure_water_density_tanaka(t)) for t in range(0, 101)])
    t_crg, d_crg = zip(*[(t, pure_water_density_craig(t)) for t in range(0, 101)])
    plt.plot(t_tnk, d_tnk, label='Tanaka et al (2001)')
    plt.plot(t_crg, d_crg, label='Craig (1961)')
    plt.title('Pure water density')
    plt.ylabel('Pure water density in mg/l')
    plt.xlabel(u'Water temperature in °C')
    plt.legend(loc='upper right')
    plt.show()


def plot_water_density_temperature_and_pressure():
    for p in np.array([0.0, 10.0, 100.0]):
        t, d = zip(*[(t, water_density(t, 0.0, p * 100000.0)) for t in range(0, 101)])
        plt.plot(t, d, label='P=' + str(p) + ' bar')
    plt.title('Water density')
    plt.ylabel('Water density in mg/l')
    plt.xlabel(u'Water temperature in °C')
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.show()


def plot_water_density_temperature_and_salinity():
    for s in np.arange(0.0, 35.0, 5.0):
        t, d = zip(*[(t, water_density(t, s, 0.0)) for t in range(0, 101)])
        plt.plot(t, d, label='S=' + str(s))
    plt.title('Water density')
    plt.ylabel('Water density in mg/l')
    plt.xlabel(u'Water temperature in °C')
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()


def plot_water_saturation_vapour_pressure():
    t, d = zip(*[(t, math.log(1000.0 * water_saturation_vapour_pressure(t))) for t in range(0, 101)])
    plt.plot(t, d)
    plt.title('Water vapour pressure')
    plt.ylabel('Water vapour pressure in kPa')
    plt.xlabel(u'Water temperature in °C')
    plt.grid(True)
    plt.show()


def plot_water_saturation_vapour_pressure_comparison():
    f = 0.001  # kPa
    t_iapws, d_iapws = zip(*[(t, f * water_saturation_vapour_pressure_iapws(t)) for t in range(0, 101)])
    t_cimo, d_cimo = zip(*[(t, f * water_saturation_vapour_pressure_cimo(t)) for t in range(0, 101)])
    t_wmo, d_wmo = zip(*[(t, f * water_saturation_vapour_pressure_wmo(t)) for t in range(0, 101)])
    plt.plot(t_iapws, d_iapws, label='IAPWS')
    plt.plot(t_cimo, d_cimo, label='CIMO')
    plt.plot(t_wmo, d_wmo, label='WMO')
    plt.title('Water saturation vapour pressure')
    plt.ylabel('Water vapour pressure in kPa')
    plt.xlabel(u'Water temperature in °C')
    plt.legend(loc='upper right')
    plt.show()

