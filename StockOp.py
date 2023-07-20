#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import pandas as pd
import numpy as np
from StockQuery import StockQuery
from Utils import RecTime
import sys

class StockOp:
    def __init__(self, i, chg_perc, interval, start_date, end_date):
        if isinstance(i, str):
            self.ts_code = i
            self.name = ''
            self.industry = ''
            self.begin_mv = 0.0
        elif isinstance(i, dict):
            self.ts_code = i['ts_code']
            self.name = i['name']
            self.industry = i['industry']
            self.begin_mv = i['mktvalue']
        else:
            return

        print('__init__', self.ts_code)
        self.start_date = start_date
        self.end_date = end_date

        # 设置初始参数, 整个过程，多次交易不改变
        self.chg_perc = chg_perc
        self.interval = interval
        self.dec_buy_ratio = 5
        self.df_stat = pd.DataFrame()

        # 设置初始参数, 整个过程，多次交易不断累加
        self.accum_profit = 0.0
        self.max_cost = 0.0

        # 每次交易都清零
        self.init_deal()

        sq = StockQuery()
        df_day   = sq.query_day_code_date_df(self.ts_code, start_date, end_date) 
        df_bonus = sq.query_bonus_code_df(self.ts_code)

        self.day_df = pd.DataFrame()
        self.bonus_df = pd.DataFrame()
        if df_day.empty:
            return
        self.day_df = df_day[(df_day["date"] >= start_date) & (df_day["date"] <= end_date)]
        self.bonus_df = df_bonus

        d0 = df_day.iloc[-1]
        d0_mktvalue = d0['volume']/(d0['turnoverrate']/100) * d0['close']
        self.mktvalue = d0_mktvalue

        df_bd = sq.query_bd(self.ts_code.split('.')[0])
        self.pe = 0
        if not df_bd.empty:
            self.pe = df_bd.iloc[0]['市盈率']

    def __del__(self):
        if self.day_df is not None:
            del self.day_df
        if self.bonus_df is not None:
            del self.bonus_df

    # 每次卖出后的清零
    def init_deal(self):
        self.first_buy_price = 0.0
        self.first_buy_date = ""
        self.next_buy_price = 9999.0
        self.next_buy_qty = 100
        self.buy_count = 0

        self.min_price = 9999.0
        self.min_date = ""
        self.sell_exp_price = 0.0

        self.accum_cost = 0.0
        self.accum_qty = 0

    # 价格除权
    def xd(self, ori_p, xd):
        date = str(xd["date"].values[0])
        base = float(xd["base"])
        bonus = float(xd['bonus'])
        free = float(xd['free'])
        new = float(xd['new'])
        new_p = (ori_p * base - bonus) / (base+free+new)
        new_p = round(new_p, 4)
        ##print('xd {:.3f} -> {} {} ({} {} {} {})'.format(ori_p, new_p, date, base, bonus, free, new))
        return new_p
        
    def push_stat(self, date, cur_profit):
        self.df_stat = self.df_stat.append(
            {"date": date, 
            "first_buy_price": self.first_buy_price,
            "first_buy_date": self.first_buy_date,
            "min_price": self.min_price,
            "min_date": self.min_date,
            "buy_count": self.buy_count,
            "accum_cost": self.accum_cost,
            "accum_qty": self.accum_qty,
            "sell_price": self.sell_exp_price,
            "sell_date": date,
            "profit": cur_profit}, 
            ignore_index=True)

    def process_day(self):
        if self.day_df.empty:
            return
        rt = RecTime()
        # 遍历每一天
        for i, row in self.day_df.iterrows():
            date = row["date"]

            # 判断是否存在除权的情况
            if not self.bonus_df.empty:
                bonus = self.bonus_df[self.bonus_df["date"] == date]
                if len(bonus) > 0:
                    if self.buy_count != 0: # 还未开始first_buy也无需除权
                        # method1: XD the original value
                        self.min_price = self.xd(self.min_price, bonus)
                        self.first_buy_price = self.xd(self.first_buy_price, bonus)
                        self.sell_exp_price = self.min_price * self.chg_perc
                        self.next_buy_price = self.first_buy_price * (1-self.interval*self.buy_count)

                        # method2: XD the current value
                        # 这个逻辑有矛盾，虽然这次next_buy进行了除权
                        # 但下一次买时，next_buy会按照first_buy计算，和这次XD完全无关了，肯定没道理
                        '''
                        self.sell_exp_price = self.xd(self.sell_exp_price, bonus)
                        self.next_buy_price = self.xd(self.next_buy_price, bonus)
                        '''

                        #print('{} XD first/min/next/sell {:.3f} {:.3f} {:.3f}({}) {:.3f}'.format(date, self.first_buy_price, self.min_price, self.next_buy_price, self.next_buy_qty, self.sell_exp_price))
                    else:
                        #print(f'{date} XD still no first buy')
                        pass

            # 更新最低价、卖出价
            if row["low"] < self.min_price:
                ##print('min {} {} -> {}'.format(date, self.min_price, row["low"]))
                self.min_price = row["low"]
                self.min_date = date
                self.sell_exp_price = self.min_price * self.chg_perc

            # 判断是否卖出
            if row["high"] >= self.sell_exp_price:
                cur_profit = self.sell_exp_price * self.accum_qty - self.accum_cost
                self.accum_profit += cur_profit
                if self.max_cost < self.accum_cost:
                    self.max_cost = self.accum_cost
                #print('{} sell {:.2f} = {:.2f} * {:.1f} - {:.2f}'.format(date, cur_profit, self.sell_exp_price, self.accum_qty, self.accum_cost))

                self.push_stat(date, cur_profit)
                self.init_deal()
                continue

            # 判断是否买入
            while row["low"] <= self.next_buy_price:
                if self.buy_count == 0:
                    self.first_buy_price = (row["low"] + row["high"]) / 2
                    self.first_buy_date = date
                    self.next_buy_price = self.first_buy_price
                self.accum_cost += self.next_buy_price * self.next_buy_qty
                self.accum_qty += self.next_buy_qty
                self.buy_count += 1
                #print('{} buy {} {:.3f} {:.1f}'.format(date, self.buy_count, self.next_buy_price, self.next_buy_qty))

                self.next_buy_price = self.first_buy_price * (1-self.interval*self.buy_count)
                self.next_buy_qty = np.round(np.exp2(self.buy_count/self.dec_buy_ratio))*100
        
        if self.buy_count != 0:
            self.push_stat(np.nan, np.nan)
            if self.max_cost < self.accum_cost:
                self.max_cost = self.accum_cost

        rt.show_ms()

    def show_stat(self):
        print('{} {}-{} {} {}'.format(self.ts_code, self.start_date, self.end_date, self.chg_perc, self.interval))
        if self.day_df.empty:
            print('day_df empty')
            print()
            return
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', -1):
            print(self.df_stat)

        today_df = self.day_df[self.day_df["date"] == self.end_date]
        if today_df.empty:
            print(self.day_df)
            return
        day = today_df.iloc[-1]

        if self.df_stat.empty:
            print('{} {} {:.0f} {} no profit first day?'.format(self.ts_code, self.name, self.mktvalue, self.pe))
            return

        last = self.df_stat.iloc[-1]
        unit_cost = last['accum_cost']/last['accum_qty']
        cur_profit = (day['high'] - unit_cost)*last['accum_qty']

        norm_co = self.max_cost/1000000
        norm_accum_profit = self.accum_profit/norm_co
        norm_cur_profit = cur_profit/norm_co

        print('{} {} {} {:.1f}({:.1f}) {}'.format(self.ts_code, self.name, self.industry, self.mktvalue/100000000, self.begin_mv, self.pe), end=' ')
        print('profit {:.0f} {:.0f}'.format(self.accum_profit, cur_profit), end=' ')
        print('norm {:.0f} {:.0f}'.format(norm_accum_profit, norm_cur_profit), end=' ')
        print('max_cost {:.0f}'.format(self.max_cost), end=' ')

        if pd.isna(last['date']):
            print('hold {:.2f}*{:.0f}({}-{})'.format(
                unit_cost, last['accum_qty'], day['low'], day['high']))
        print()
        return

if __name__ == '__main__':
    rt = RecTime()
    sq = StockQuery()

    # 一个code
    #so = StockOp("600938.SH", chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230630")
    '''
    ts_code    = '002456.SZ' # 欧菲光
    ts_code    = '300476.SZ'
    ts_code = '601398.SH'
    ts_code = '601857.SH'
    so = StockOp(ts_code, chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230717")
    so.process_day()
    so.show_stat()
    quit()
    '''

    # 固定列表
    '''
    code_list = [
            '002315.SZ',
            '002919.SZ',
            '300211.SZ',
            '300476.SZ',
            '300620.SZ',
            '300654.SZ',
            '300678.SZ',
            '301052.SZ',
            '301179.SZ',
            '301312.SZ',
            '600666.SH',
            '688160.SH'
        ]
    for item in code_list:
        so = StockOp(item, chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230717")
        so.process_day()
        so.show_stat()
        del so
    quit()
    '''

    # 查询
    '''
    code_list = sq.query_basic(None)
    # 一旦出现异常，可以恢复到异常发生时的代码继续
    stock_codes = [item['ts_code'] for item in code_list]
    start_code = '688627.SH'
    start_index = stock_codes.index(start_code)
    start_index = 0
    for i in range(start_index, len(code_list)):
        so = StockOp(code_list[i]['ts_code'], chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230717")
        so.process_day()
        so.show_stat()
        del so
        quit()
    '''

    # 采用mktvalue进行筛选
    if len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date   = sys.argv[2]
    #v1 = 10000; v2 = np.inf # 市值超过万亿的：中国石油，贵州茅台，工商银行，其中工商银行基本不波动，没有盈利空间
    v1 = 0; v2 = np.inf # 市值超过万亿的：中国石油，贵州茅台，工商银行，其中工商银行基本不波动，没有盈利空间
    code_list = sq.query_mktvalue(start_date, v1, v2)
    stock_codes = [item['ts_code'] for item in code_list]
    start_index = 0
    #start_index = stock_codes.index('601398.SH')
    for i in range(start_index, len(code_list)):
        so = StockOp(code_list[i], chg_perc=1.55, interval=0.03, start_date=start_date, end_date=end_date)
        so.process_day()
        so.show_stat()
        del so

    rt.show_s()
