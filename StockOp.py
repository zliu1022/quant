#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import pandas as pd
import numpy as np
from StockQuery import StockQuery
from Utils import RecTime

class StockOp:
    def __init__(self, i, chg_perc, interval, start_date, end_date):
        ts_code = i['ts_code']
        print('__init__', ts_code)
        self.ts_code = ts_code
        self.name = i['name']
        self.industry = i['industry']
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
        df_day   = sq.query_day_code_date_df(ts_code, start_date, end_date) 
        df_bonus = sq.query_bonus_code_df(ts_code)

        self.day_df = pd.DataFrame()
        self.bonus_df = pd.DataFrame()
        if df_day.empty:
            return
        self.day_df = df_day[(df_day["date"] >= start_date) & (df_day["date"] <= end_date)]
        self.bonus_df = df_bonus

        d0 = df_day.iloc[-1]
        d0_mktvalue = d0['volume']/(d0['turnoverrate']/100) * d0['close']
        self.mktvalue = d0_mktvalue

        df_bd = sq.query_bd(i['symbol'])
        print(len(df_bd.index))
        print(df_bd)
        self.pe = df_bd[0]['市盈率']
        quit()

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
        last = self.df_stat.iloc[-1]
        unit_cost = last['accum_cost']/last['accum_qty']
        profit = (day['high'] - unit_cost)*last['accum_qty']
        print('{} {} {} {:.0f} {}'.format(self.ts_code, self.name, self.industry, self.mktvalue, self.pe), end=' ')
        print('profit {:.0f} {:.0f}'.format(self.accum_profit, profit), end=' ')
        print('max_cost {:.0f}'.format(self.max_cost), end=' ')
        if pd.isna(last['date']):
            print('hold {:.2f}*{:.0f}({}-{})'.format(
                unit_cost, last['accum_qty'], day['low'], day['high']))
        print()
        return

if __name__ == '__main__':
    #so = StockOp("600938.SH", chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230630")
    #so.process_day()
    #quit()
    rt = RecTime()
    code_list = [
            {'ts_code': '002315.SZ'},
            {'ts_code': '002919.SZ'},
            {'ts_code': '300211.SZ'},
            {'ts_code': '300476.SZ'},
            {'ts_code': '300620.SZ'},
            {'ts_code': '300654.SZ'},
            {'ts_code': '300678.SZ'},
            {'ts_code': '301052.SZ'},
            {'ts_code': '301179.SZ'},
            {'ts_code': '301312.SZ'},
            {'ts_code': '600666.SH'},
            {'ts_code': '688160.SH'}
        ]
    sq = StockQuery()
    code_list = sq.query_basic(None)
    '''
    stock_codes = [item['ts_code'] for item in code_list]
    start_code = '688627.SH'
    start_index = stock_codes.index(start_code)
    for i in range(start_index, len(code_list)):
        so = StockOp(code_list[i]['ts_code'], chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230717")
    '''
    for item in code_list:
        so = StockOp(item, chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230717")
        so.process_day()
        so.show_stat()
        del so
        quit()
    rt.show_s()
    quit()

    ts_code    = '002456.SZ' # 欧菲光
    ts_code    = '300476.SZ' # 欧菲光
    so = StockOp(ts_code, chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230717")
    so.process_day()
    so.show_stat()

