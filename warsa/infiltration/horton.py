__author__ = 'roehrig'

from math import exp, log, fabs
import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset

pd.set_option('display.width', 200)


class Horton:

    def __init__(self, f0, fc, kp):
        self.f0 = f0  # mm/h
        self.fc = fc  # mm/h
        self.kp = kp  # 1/h
        self.dt1h = np.timedelta64(1, 'h')

    def get_infiltration(self, t, t0, k=None):
        if not k:
            k = self.kp
        dtt0 = (t - t0) / self.dt1h
        return self.fc + (self.f0 - self.fc) * exp(-k * dtt0)

    def get_cumulative_infiltration(self, t, t0, k=None):
        if not k:
            k = self.kp
        return self.fc * (t - t0) + (self.f0 - self.fc) * (1 - exp(-k * (t - t0))) / k

    def get_infiltration_increment(self, ti, tj, t0, k=None):
        if not k:
            k = self.kp
        dtji = (tj - ti) / self.dt1h
        dti0 = (ti - t0) / self.dt1h
        dtj0 = (tj - t0) / self.dt1h
        return self.fc * dtji + (self.f0 - self.fc) * (exp(-k * dti0) - exp(-k * dtj0)) / k

    def get_t0(self, f, t, k=None):
        if not k:
            k = self.kp
        dt = log((f - self.fc)/(self.f0 - self.fc)) / k
        return t + DateOffset(hours=dt)

    def get_infiltration_above_capacity(self, fi, ti, tj):
        t0 = self.get_t0(fi, ti)
        fj = self.get_infiltration(tj, t0)
        ffj = self.get_infiltration_increment(ti, tj, t0)
        return fj, ffj

    def get_infiltration_below_capacity(self, fi, ti, tj, i):
        dth = 1.0/240.0  # interval in hours (0.25 minute)
        dt = DateOffset(hours=dth)  #  date offset in hours
        rd = i * dth
        kpd = self.kp * rd  # kp ir rain depth in the interval
        fl = fk = fi
        ffl = 0.0
        if i > 0.0:
            tk, tl = ti, ti + dt
            while tl < tj:
                ffp = self.get_infiltration_increment(tk, tl, self.get_t0(fk, tk))
                kkl = kpd / ffp
                fl = self.get_infiltration(tl, self.get_t0(fk, tk, kkl), kkl)
                ffl += rd
                if i >= fl:  # ponds
                    return fl, ffl, tl
                tk, tl, fk = tl, tl + dt, fl
        return fl, i * ((tj - ti) / self.dt1h), tj  # tj: does not pond

    def calculate_infiltration(self, df):
        df['tj'] = df.index
        df['ti'] = df['tj'].shift(1)
        fj = self.f0
        ff_acc = 0.0
        f_list = [np.NaN]
        ff_list = [np.NaN]
        for i in range(1, len(df)):
            r = df.iloc[i]
            ti, tj, i = r.ti, r.tj, r.i
            fi = fj
            if i < fi:
                fj, ffj, tj0 = self.get_infiltration_below_capacity(fi, ti, tj, i)
                if i >= fj:
                    ffj_tmp = ffj
                    fj, ffj = self.get_infiltration_above_capacity(fi, ti, tj)
                    ffj += ffj_tmp
            else:
                fj, ffj = self.get_infiltration_above_capacity(fi, ti, tj)
            ff_acc += ffj
            f_list.append(fj)
            ff_list.append(ffj)
        df['f'] = f_list
        df['df'] = ff_list
        df['cdf'] = df['df'].cumsum()
        df['r'] = (df['d'] - df['df']).round(6)
        df[df['r'] < 0] = 0.0
        del df['tj']
        del df['ti']

import datetime
def test1():
    # http://www.engr.colostate.edu/~ramirez/ce_old/classes/cive322-Ramir
    fo, fc, kp = 80, 12.5, 3.0  # mm/h, mm/h, 1/h
    tti = [
        [datetime.datetime(2000, 1, 1, 0, 00),  np.NaN],  # min., min., i [mm/h]
        [datetime.datetime(2000, 1, 1, 0, 10), 15.0],
        [datetime.datetime(2000, 1, 1, 0, 20), 30.0],
        [datetime.datetime(2000, 1, 1, 0, 30), 80.0],
        [datetime.datetime(2000, 1, 1, 0, 40), 50.0],
        [datetime.datetime(2000, 1, 1, 0, 50), 40.0],
        [datetime.datetime(2000, 1, 1, 1, 00), 30.0],
        [datetime.datetime(2000, 1, 1, 1, 10),  8.0],
        [datetime.datetime(2000, 1, 1, 1, 20),  0.0],
        [datetime.datetime(2000, 1, 1, 1, 30),  0.0],
        [datetime.datetime(2000, 1, 1, 1, 40),  0.0],
        [datetime.datetime(2000, 1, 1, 1, 50),  0.0],
        [datetime.datetime(2000, 1, 1, 2, 00),  0.0]
    ]
    df = pd.DataFrame(tti, columns=['Date', 'i']).set_index('Date')
    df['d'] = df['i'] / 6.0
    df['cd'] = df['d'].cumsum()
    horton = Horton(fo, fc, kp)
    horton.calculate_infiltration(df)
    print df
    df[['d', 'r']].plot()
    import matplotlib.pyplot as plt
    plt.show()

# test1()
