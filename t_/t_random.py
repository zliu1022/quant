#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import random

sample_num = 10000

low  = 30
high = 40

y = []

y1 = []
for _ in range(sample_num):
    y1.append(random.randint(low,  high))
y.append(y1)

y2 = []
for _ in range(sample_num):
    y2.append(random.uniform(low, high))
y.append(y2)

y3 = []
for _ in range(sample_num):
    y3.append(round(random.uniform(low, high), 1))
    #y3.append(random.uniform(low*100, high*100))
y.append(y3)

# -3 ~ 3 正态分布
y4 = np.random.randn(sample_num)
y.append(y4)

plt.style.use('seaborn-whitegrid')

'''
for i in range(len(y)):
    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1,  0.9, 0.9])
    #ax.hist(y[i], bins=40, histtype='stepfilled', alpha=0.3, density=True, edgecolor='black', label='hist')
    ax.hist(y[i], bins=40, histtype='stepfilled', alpha=0.3, density=True, edgecolor='black', label='hist')
    plt.show()
'''

fig = plt.figure()
ax1 = fig.add_axes([0.05, 0.05,  0.4, 0.4]) # left-bottom
ax2 = fig.add_axes([0.05, 0.55,  0.4, 0.4]) # left-top
ax3 = fig.add_axes([0.55, 0.55,  0.4, 0.4]) # right-top
ax4 = fig.add_axes([0.55, 0.05,  0.4, 0.4]) # right-bottom

ax1.hist(y[0], bins=80, histtype='stepfilled', alpha=0.3, density=True, edgecolor='black', label='randint')
ax1.set_title('random.randint')

ax2.hist(y[1], bins=40, histtype='stepfilled', alpha=0.5, density=True, edgecolor='red', label='hist')
ax2.set_title('random.uniform')

ax3.hist(y[2], bins=100, histtype='stepfilled', alpha=1, density=False, edgecolor='black', label='hist')
ax3.set_title('round(random.uniform, 1)')

ax4.hist(y[3], bins=40, histtype='stepfilled', alpha=0.1, density=True, edgecolor='black', label='hist')
ax4.set_title('np.random.randn')
plt.show()
