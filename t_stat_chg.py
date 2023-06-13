#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from StockQuery import StockQuery
from StockRecover import recover_price_forward
from StockSim import f2exp10
from StockSim import stat_chg
from StockSim import sim_chg_single

if __name__ == '__main__':
    sq = StockQuery()

    # 检查复权数据，amount不复权
    start_date = '20200101'
    end_date   = '20230602'
    chg_perc   = 0.55
    interval   = 0.03

    #ts_code    = '601919.SH' 前复权出现负值
    '''
    sq = StockQuery()
    ret = sq.check_bad_bonus(ts_code)
    df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date)
    df_bonus = sq.query_bonus_code_df(ts_code)
    df_forw  = recover_price_forward(df_day, df_bonus)
    len_after_dot, m_10 = f2exp10(interval)
    df_chg, inc_num, max_dec_perc, max_dec_days = stat_chg(df_forw, start_date, chg_perc)
    '''

    ts_code    = '831726.BJ'  # max_cost 出现0
    ret = sim_chg_single(sq, ts_code, start_date, end_date, chg_perc, interval)
    print(ret)
