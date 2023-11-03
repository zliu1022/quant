#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# Define the data series
series_data = {
    #"s1": [100.0, 95.23, 118.56, 95.23, 86.35, 107.5, 86.35, 78.3, 97.48, 78.3, 71.0, 88.39, 71.0, 64.38, 80.15, 64.38, 58.37, 72.67, 58.37, 52.92, 65.88, 52.92, 47.98, 59.73, 47.98, 43.51, 54.16, 43.51, 39.45, 49.11, 39.45, 35.76, 44.52, 35.76, 32.42, 40.36, 32.42, 29.39, 36.59, 29.39, 26.64, 33.16],
    "s2": [100.0, 90.68, 112.89, 90.68, 78.3, 97.48, 78.3, 67.61, 84.17, 67.61, 58.37, 72.67, 58.37, 50.39, 62.73, 50.39, 43.51, 54.16, 43.51, 37.56, 46.76, 37.56, 32.42, 40.36, 32.42, 27.98, 34.83, 27.98, 24.15, 30.06, 24.15, 20.84, 25.94, 20.84, 17.98, 22.38, 17.98, 15.52, 19.32, 15.52, 13.38, 16.65],
    #"s3": [100.0, 86.35, 107.5, 86.35, 71.0, 88.39, 71.0, 58.37, 72.67, 58.37, 47.98, 59.73, 47.98, 39.45, 49.11, 39.45, 32.42, 40.36, 32.42, 26.64, 33.16, 26.64, 21.89, 27.25, 21.89, 17.98, 22.38, 17.98, 14.77, 18.38, 14.77, 12.13, 15.1, 12.13, 9.96, 12.4],
    #"s4": [100.0, 82.23, 102.37, 82.23, 64.38, 80.15, 64.38, 50.39, 62.73, 50.39, 39.45, 49.11, 39.45, 30.87, 38.43, 30.87, 24.15, 30.06, 24.15, 18.89, 23.51, 18.89, 14.77, 18.38, 14.77, 11.55, 14.37, 11.55, 9.02, 11.22],
    "s5": [100.0, 78.3, 97.48, 78.3, 58.37, 72.67, 58.37, 43.51, 54.16, 43.51, 32.42, 40.36, 32.42, 24.15, 30.06, 24.15, 17.98, 22.38, 17.98, 13.38, 16.65, 13.38, 9.96, 12.4],
}

# Initialize the plot for all series
plt.figure(figsize=(15, 10))
plt.title('All Series with Arrows')

# Loop through each series
for series_name, data in series_data.items():
    # Create the smooth curve with dashed line style
    x = np.linspace(0, len(data)-1, len(data))
    x_smooth = np.linspace(0, len(data)-1, 300)
    y_smooth = make_interp_spline(x, data)(x_smooth)
    plt.plot(x_smooth, y_smooth, '--', label=f'Smooth Curve of {series_name}')

    # Initialize storage for previous ranges for downward arrows
    prev_ranges = []

    # Add arrows between points
    for i in range(len(data) - 1):
        color = 'red' if data[i+1] > data[i] else 'blue'

        # Check for overlapping downward ranges only if the arrow is blue
        if color == 'blue':
            overlap = False
            for r in prev_ranges:
                if max(data[i+1], data[i]) <= r[0] and min(data[i+1], data[i]) >= r[1]:
                    overlap = True
                    break
            if not overlap:
                plt.annotate('', xy=(i+1, data[i+1]), xytext=(i, data[i]), arrowprops=dict(arrowstyle='->,head_width=0.5,head_length=1', lw=2, color=color))
                prev_ranges.append((max(data[i], data[i+1]), min(data[i], data[i+1])))
        else:
            # Draw upward arrows without overlap check
            plt.annotate('', xy=(i+1, data[i+1]), xytext=(i, data[i]), arrowprops=dict(arrowstyle='->,head_width=0.5,head_length=1', lw=2, color=color))

            # Remove any previous downward range that overlaps with the current upward arrow
            prev_ranges = [r for r in prev_ranges if not (max(data[i+1], data[i]) >= r[0] and min(data[i+1], data[i]) <= r[1])]

# Add labels and legends
plt.xlabel('Time')
plt.ylabel('Value')
plt.legend()

# Show the plot
plt.show()

