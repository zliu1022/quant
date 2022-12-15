#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import math
import random

def f2exp10(f_num):
    # f_num 是浮点数，返回：小数点后有效数字个数，转成10的次方
    str_ivl = str(f_num)
    len_after_dot = len(str_ivl) - str_ivl.find('.') -1
    m_10 = 10 ** len_after_dot
    return len_after_dot,m_10

def step_num(dec_input, interval):
    # 最接近 input 的 interval整数倍的数
    len_after_dot, m_10 = f2exp10(interval)
    mid_ret = math.floor(dec_input/100/interval)
    dec_perc = math.floor((mid_ret*interval+0.000001)*m_10)/m_10
    return dec_perc, mid_ret

dec_input = float(46.949025)
interval = 0.03
dec_output,mid_ret = step_num(dec_input, interval)
print('{} {} {}({:.5f}-{:.5f}'.format(dec_input, interval, dec_output, dec_output-interval, dec_output+interval))

dec_input =float(57.255362)
interval = 0.037
dec_output,mid_ret = step_num(dec_input, interval)
print('{} {} {}({:.5f}-{:.5f}'.format(dec_input, interval, dec_output, dec_output-interval, dec_output+interval))

dec_input =float(57)
interval = 0.03
dec_output,mid_ret = step_num(dec_input, interval)
print('{} {} {}({:.5f}-{:.5f}'.format(dec_input, interval, dec_output, dec_output-interval, dec_output+interval))

dec_input =float(14.331983805668013)
interval = 0.02
dec_output,mid_ret = step_num(dec_input, interval)
print('{} {} {}({:.5f}-{:.5f} {}'.format(dec_input, interval, dec_output, dec_output-interval, dec_output+interval, mid_ret))

if __name__ == '__main__':
    quit()
