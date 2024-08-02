#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt

import math
def round_up(number):
    #if np.isinf(number): return -1
    if number > 0:
        return math.floor(number + 0.5)
    elif number < 0:
        # 负数的处理方式不同，需要使用math.ceil
        return math.ceil(number - 0.5)
    else:
        return 0

# Constants for the sequences
initial_value = 100
decay_percentage_one = 1 - 4.77 / 100  # Conversion to decimal
decay_value_two = 3 / 100  # Conversion to decimal

# Generate Sequence One
def seqv2(initial_value, decay_percentage_one, total_num):
    seq = [initial_value]
    for _ in range(total_num):
        next_value = seq[-1] * decay_percentage_one
        seq.append(round_up(next_value*100)/100)
    return seq

sequence_one = seqv2(initial_value, decay_percentage_one, 37)
seq_3 = seqv2(initial_value, (1-3/100), 37)
seq_65 = seqv2(initial_value, (1-6.5/100), 37)

# Generate Sequence Two
sequence_two = [round_up((initial_value * (1 - i * decay_value_two))*100)/100 for i in range(35)]

# 获取数组长度
min_len = min(len(sequence_one), len(sequence_two))

print("| no | 等比4.77% | 相邻差值 | 等差3% | 相邻差值 |")
print("| :-: | :-: | :-: | :-: | :-: |")
# 按索引顺序打印每个数组的值
for i in range(min_len):
    '''
    print(f"{i} {sequence_one[i]:.2f}, \
        {sequence_one[i]-sequence_one[i-1] if i>0 else '---'}, \
        {sequence_two[i]:.2f}", \
        {sequence_two[i]-sequence_two[i-1] if i>0 else '---'})
    '''
    seq1_value = f"{sequence_one[i]:.2f}"
    seq1_diff = f"{sequence_one[i] - sequence_one[i-1]:.2f}" if i > 0 else "---"
    seq2_value = f"{sequence_two[i]:.2f}"
    seq2_diff = f"{sequence_two[i] - sequence_two[i-1]:.2f}" if i > 0 else "---"
    print(f"| {i} | {seq1_value} | {seq1_diff} | {seq2_value} | {seq2_diff} |")

# Define the sequences
'''
sequence_one = [
    100, 97, 94, 91, 88, 85, 82, 79, 76, 73, 70, 67, 64, 61, 58, 55, 52, 49
]
sequence_two = [
    100, 95.23, 90.69, 86.36, 82.24, 78.32, 74.58, 71.03, 67.64, 64.41, 61.34,
    58.41, 55.63, 52.97, 50.45
]
'''

dot_size = 10

# Plot the sequences
plt.figure(figsize=(10, 8))

plt.rcParams['font.sans-serif'] = ['Songti SC']  # 设置中文字体为宋体
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号

# Sequence One
for i, value in enumerate(sequence_one):
    plt.scatter(value, value, color='blue', s=dot_size, label='优化后的等比买入数列，Geometric Decay Sequence a_n=a_n-1*(1-4.77)%' if i == 0 else "")
    plt.text(value+1, value, f'{i+1}', color='darkblue', fontsize=9, ha='center', va='center')

# blue, green, red, cyan, magenta, yellow, orange, brown, lime
for i, value in enumerate(seq_3):
    plt.scatter(5, value, color='cyan', s=dot_size, label='等比，a_n=a_n-1*(1-3)%' if i == 0 else "")
for i, value in enumerate(sequence_one):
    plt.scatter(10, value, color='orange', s=dot_size, label='等比，a_n=a_n-1*(1-4.77)%' if i == 0 else "")
for i, value in enumerate(seq_65):
    plt.scatter(15, value, color='green', s=dot_size, label='等比，a_n=a_n-1*(1-6.5)%' if i == 0 else "")

# Sequence Two
for i, value in enumerate(sequence_two):
    plt.scatter(value, value, color='red', s=dot_size, label='一开始的等差买入数列，Linear Decay Sequence a_n=a0*(1-n*3)%' if i == 0 else "")
    plt.text(value-1, value, f'{i+1}', color='darkred', fontsize=9, ha='center', va='center')

plt.axhline(y=50, color='green', linestyle='--', linewidth=1)
plt.axhline(y=25, color='green', linestyle='--', linewidth=1)
plt.axhline(y=17.27, color='green', linestyle='--', linewidth=1)

# Set up the graph
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Scatter Plot of Two Sequences')
plt.legend()
plt.grid(True)

# Reverse the X-axis to show decreasing values from left to right
plt.xlim(105, 0)
plt.ylim(105, 10)
plt.gca().invert_yaxis()

# Show the plot
plt.show()

