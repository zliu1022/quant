#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
import numpy as np

if __name__ == '__main__':
    sq = StockQuery()

    # query dayline
    ts_code    = '601919.SH'
    start_date = '20200101'
    end_date   = '20200101'
    #ref = sq.query_day_code_date(ts_code, start_date, end_date)

    # select mktvalue [0, 10) 亿
    v1 = 0; v2 = 10
    ref = sq.select_mktvalue(v1, v2)
    print('[{:4d},   {:4d}) {:4d}'.format(v1, v2, len(ref)))

    v1 = 10; v2 = 20
    ref = sq.select_mktvalue(v1, v2)
    print('[{:4d},   {:4d}) {:4d}'.format(v1, v2, len(ref)))

    v1 = 20; v2 = 50
    ref = sq.select_mktvalue(v1, v2)
    print('[{:4d},   {:4d}) {:4d}'.format(v1, v2, len(ref)))

    v1 = 50; v2 = 100
    ref = sq.select_mktvalue(v1, v2)
    print('[{:4d},   {:4d}) {:4d}'.format(v1, v2, len(ref)))

    v1 = 100; v2 = 200
    ref = sq.select_mktvalue(v1, v2)
    print('[{:4d},   {:4d}) {:4d}'.format(v1, v2, len(ref)))

    v1 = 200; v2 = 500
    ref = sq.select_mktvalue(v1, v2)
    print('[{:4d},   {:4d}) {:4d}'.format(v1, v2, len(ref)))

    v1 = 500; v2 = 1000
    ref = sq.select_mktvalue(v1, v2)
    print('[{:4d},   {:4d}) {:4d}'.format(v1, v2, len(ref)))

    v1 = 1000; v2 = np.inf
    ref = sq.select_mktvalue(v1, v2)
    print('[{:4d},    inf) {:4d}'.format(v1, len(ref)))

