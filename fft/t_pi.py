#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math

# when n = 1, means 4-sides square
def cal_pi_2(s, n):
    for i in range(0,n):
        d = math.sqrt(1 - (s*s/4))
        a = 1 - d
        s = math.sqrt(s*s/4 + a*a)

    num = 2*2**n # how many side
    print('sides %7d x %.12f' % (num*2, s), end=' ')
    return s * num

p_std = 3.141592653589793238462
p_zuchongzhi_min = 3.1415926
p_zuchongzhi_max = 3.1415927

for i in range (1, 19):
    p = cal_pi_2(math.sqrt(2), i)
    delta = abs(p - p_std)
    print('%.12f %.12f' % (p, delta), end=' ')
    if p > p_zuchongzhi_min and p < p_zuchongzhi_max:
        print('<- zuchongzhi reach here', end='')
        p_zuchongzhi_max = 0
    print()

