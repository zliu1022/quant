#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np

x1 = np.linspace(0, 10, 50)
y3 = 0.5 + 0.5 * np.sin(x1) + 0.1 * np.sin(50 * x1)
y4 = np.random.randn(50)

print(len(x1), len(y3), len(y4))

plt.style.use('seaborn-whitegrid')
fig = plt.figure()
ax1 = fig.add_axes([0.1, 0.3,  0.85, 0.65])

#ax1.plot(x1, y3, '.', color='black', label='sin(50x)')
#ax1.hist(y4, bins=40, histtype='stepfilled', alpha=0.3, density=True, edgecolor='black', label='hist')
ax1.bar(x1, y4, width=0.1, label='hist')
ax1.set(xlim=(-1, 11), ylim=(-3, 3), 
    xlabel='x', ylabel='g(x)',
    title='')
leg1 = ax1.legend(loc='upper right', frameon=True)

plt.show()

