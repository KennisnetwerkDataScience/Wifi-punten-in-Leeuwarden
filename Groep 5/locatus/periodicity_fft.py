import pandas as pd
import numpy as np
import scipy as sp
import scipy.fftpack
import matplotlib
import matplotlib.pyplot as plt
import datetime

from locatus.util import load_data
from locatus.util import device_time


def device_timeseries(df, addr):
    ts = device_time(df, addr)
    ts['datetime'] = pd.to_datetime(ts['DateTimeLocal'])
    ts['t'] = ts['datetime'].apply(lambda x: x.timetuple().tm_yday * 24 + x.hour)

    dc = ts.groupby(['t']).size()

    d0 = datetime.datetime(2017, 1, 1, 0, 0, 0)
    d1 = datetime.datetime(2018, 1, 1, 0, 0, 0)
    periods = int((d1 - d0).total_seconds() / 3600)

    dcf = pd.Series(dc, index=np.arange(periods)).fillna(0)
    return dcf

def plot_device_timeseries(df, addr):
    dcf = device_timeseries(df, addr)
    plt.figure(figsize=(20,4))
    dcf.plot()
    plt.savefig('results/timeseries-%s.png' % (addr))
    plt.close()

def plot_fft(dcf):
    N = dcf.shape[0]
    T = 1.0 / 24
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    yf = sp.fftpack.fft(dcf)
    plt.figure(figsize=(20,10))
    plt.grid()
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))

def plot_device_fft(df, addr):
    dcf = device_timeseries(df, addr)
    plot_fft(dcf)
    plt.savefig('results/timeseries_%s_fft.png' % (addr))
    plt.close()

if __name__ == '__main__':
    import sys
    addr = int(sys.argv[1])
    print(addr)
    df = load_data()
    df = df.loc[(df.DateTimeLocal > '2017-01-01') & (df.DateTimeLocal < '2018-01-01')]
    #addresses = df.code_address.unique()
    #for addr in addresses:
    #plot_device_timeseries(df, addr)
    plot_device_fft(df, addr)

'''
from periodicity_fft import *
from heatmap import *

periods = 24 * 7 * 52
s = pd.Series(index=np.arange(periods))
for i in range(periods):
    s[i] = int(i % 24 / 16)
    print('%s %s' % (i, i % 168))
    if (i % 168) > (168 - 24):
        s[i] = 0

for i in range(periods):
    s[i] = int(i % 168 == 167)
    print('%s %s' % (i, int(i % 168 > 160)))

plot_fft(s)
plt.show()

df =load_data()

s = device_timeseries(df, 235360)
sample_freq = sp.fftpack.fftfreq(8736, d=1./24.)
f = sp.fftpack.rfft(s)
lf = f.copy()
#lf[(np.abs(sample_freq) < .5) & (np.abs(sample_freq) > 1.5)] = 0
#lf[lf < .25] = 0
#lf[lf < .15] = 0
rsignal = sp.fftpack.irfft(lf)

rs = pd.DataFrame(0, index=np.arange(1, 53), columns=np.arange(168))
rs.shape
for i in range(0,52):
    rs.loc[i+1] = rsignal[i*168:(i+1)*168]

plot_device_heatmap(rs)
plt.show()




sample_freq = sp.fftpack.fftfreq(8736, d=1./24.)
pos_mask = np.where(sample_freq > 0)
freqs = sample_freq[pos_mask]
power = np.abs(f)
peak_freq = freqs[power[pos_mask].argmax()]
peak_freq




d = pd.DataFrame(0, index=np.arange(1, 54), columns=[0,1,2,3,4,5,6])
d[1] = 5
d[1] = 7
d = d.div(d.sum(axis=1).sum(), axis=0)
d.std(axis=0).sum()

d = pd.DataFrame(0, index=np.arange(1, 54), columns=[0,1,2,3,4,5,6])
d.iloc[1] = 5
d = d.div(d.sum(axis=1).sum(), axis=0)
d.std(axis=0).sum()
'''
