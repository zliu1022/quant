#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

N = 600
T = 1.0 / 800.0

'''
x = 2 * np.linspace(0.0, N*T, N, endpoint=False)
y = 2 * np.sin(x) + 0.1 * np.sin(50.0 * x)
'''

#x = np.arange(0, 300, 1)
x = 2 * np.linspace(0.0, N*T, N, endpoint=False)
y = np.sin(5.0*np.pi * x)
y1 = np.sin(250.0*np.pi * x)
y2= 2*y+0.1*y1

yf = fft(y)
yf1 = fft(y1)
yf2 = fft(y2)

xf = fftfreq(N, T)[:N//2]

plt.plot(x, y)
plt.plot(x, y1)
plt.plot(x, y2)
plt.show()

plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
plt.plot(xf, 2.0/N * np.abs(yf1[0:N//2]))
plt.grid()
plt.show()

plt.plot(xf, 2.0/N * np.abs(yf2[0:N//2]))
plt.grid()
plt.show()

