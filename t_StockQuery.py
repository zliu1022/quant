#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from pprint import pprint

if __name__ == '__main__':
    sq = StockQuery()

    start_date = '20230101'
    end_date   = '20230201'
    ret = sq.query_bonus_date(start_date, end_date)
    pprint(ret[0])

    ts_code    = '831445.BJ'
    start_date = '20210101'
    end_date   = '20230201'
    ret = sq.query_bonus_code_date(ts_code, start_date, end_date)
    pprint(ret[0])

