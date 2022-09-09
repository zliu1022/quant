#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

# Create some mock data
t = np.arange(0.1, 5.0, 0.02)
data1 = np.sin(2 * np.pi * t)
data2 = np.sin(2 * np.pi * t)
#data2 = np.exp(t)

fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('time (s)')
ax1.set_ylabel('exp', color=color)
ax1.plot(t, data1, color=color)
ax1.tick_params(axis='y', labelcolor=color)
plt.ylim(-1.5,1.1)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('sin', color=color)  # we already handled the x-label with ax1
ax2.bar(t, data2, 0.01, color=color)
ax2.tick_params(axis='y', labelcolor=color)
plt.ylim(-1,10)

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
