#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
import numpy as np

if __name__ == '__main__':
    sq = StockQuery()

    industry    = '铅锌'
    start_date = '20200101'
    ref = sq.query_mktvalue_industry(start_date, industry)
    print('{}  {}'.format(industry, len(ref)))
    for i in ref:
        print(i)

