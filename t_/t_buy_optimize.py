#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
设 a，
得到数列：
    100，
    100 * a（就近取整到100的倍数），
    100 * a^2（就近取整到100的倍数），
    100 * a^3（就近取整到100的倍数），
    100 * a^4（就近取整到100的倍数）
得到数列的求和

输入 v，求数值解a，使得这个数列的和最接近 v
'''

def sequence_terms_v2(a):
    """Return the sequence terms based on value of a, with updated rounding logic."""
    return [
        100,
        int(100 * a / 100 + 0.5) * 100,
        int(100 * a ** 2 / 100 + 0.5) * 100,
        int(100 * a ** 3 / 100 + 0.5) * 100,
        int(100 * a ** 4 / 100 + 0.5) * 100
    ]

def find_a_and_sequence_closest_to_v_v2(v, step=0.001, a_range=(0, 5)):
    """Find the a value and sequence such that the sequence sum is closest to v with updated logic."""
    min_diff = float('inf')
    best_a = None
    best_sequence = None

    # Search in the given range with the given step size
    for a in [i*step for i in range(int(a_range[0]/step), int(a_range[1]/step))]:
        terms = sequence_terms_v2(a)
        seq_sum = sum(terms)
        diff = abs(seq_sum - v)

        if diff < min_diff:
            min_diff = diff
            best_a = a
            best_sequence = terms

    return best_a, best_sequence, sum(best_sequence)

# Test with the provided value
v = float(input("请输入v的值: "))
print(find_a_and_sequence_closest_to_v_v2(v))

