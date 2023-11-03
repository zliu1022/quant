#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 为X和Y生成值
x = np.linspace(0, 5, 100)
y = np.linspace(0, 5, 100)

X, Y = np.meshgrid(x, y)

# 计算Z1和Z2的值
Z1 = np.sin(np.sqrt(X**2 + Y**2))
Z2 = np.cos(np.sqrt(X**2 + Y**2))

# 创建3D图
fig = plt.figure(figsize=(12, 6))

# 绘制Z1
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(X, Y, Z1, cmap='viridis', alpha=0.6)
ax1.set_title('Surface Plot of Z1')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z1')

# 绘制Z2
ax2 = fig.add_subplot(122, projection='3d')
ax2.plot_surface(X, Y, Z2, cmap='magma', alpha=0.6)
ax2.set_title('Surface Plot of Z2')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z2')

plt.tight_layout()
plt.show()

