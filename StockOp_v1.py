#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import sys
from datetime import datetime, timedelta
import re
from pymongo import MongoClient
from StockQuery import StockQuery
from Utils import RecTime

class StockOp:
    def __init__(self, ts_code):
        self.ts_code = ts_code
        self.dec_buy_ratio = 5
        self.df_stat = pd.DataFrame()
        self.accum_profit = 0.0
        self.max_cost = 0.0

        # 每次交易都清零
        self.init_deal()

        # 读取全部日线信息
        sq = StockQuery()
        self.df_allday = sq.query_day_code_df(ts_code)
        self.bonus_df = sq.query_bonus_code_df(self.ts_code)

    # 每次卖出后的清零
    def init_deal(self):
        self.first_buy_price = 0.0
        self.first_buy_date = ""
        self.next_buy_price = 9999.0
        self.next_buy_qty = 100
        self.buy_count = 0

        self.first_buy_price_forsell = 0.0
        self.min_price_forsell = 9999.0

        self.min_price = 9999.0
        self.min_date = ""
        self.sell_exp_price = 0.0

        self.accum_cost = 0.0
        self.accum_qty = 0

    # 价格除权
    def xd(self, ori_p, xd, debug=0):
        date = str(xd["date"].values[0])
        base = float(xd["base"].iloc[0])
        bonus = float(xd['bonus'].iloc[0])
        free = float(xd['free'].iloc[0])
        new = float(xd['new'].iloc[0])
        new_p = (ori_p * base - bonus) / (base+free+new)
        new_p = round(new_p, 4)
        if debug:
            print('        {} xd {:.3f} -> {:.3f} ({} {} {} {})'.format(date, ori_p, new_p, base, bonus, free, new))
        return new_p
        
    def push_stat(self, date, cur_profit):
        if isinstance(date, str):
            min_d = datetime.strptime(self.min_date, "%Y%m%d")
            max_d = datetime.strptime(date, "%Y%m%d")
            min_max_days = (max_d - min_d).days
        else:
            min_max_days = np.nan

        new_data = {
            "date":            date, 
            "first_buy_price": round(self.first_buy_price,2),
            "first_buy_date": self.first_buy_date,
            "min_price":      round(self.min_price,2),
            "min_date":       self.min_date,
            "buy_count":      self.buy_count,
            "accum_cost":     round(self.accum_cost,2),
            "accum_qty":      self.accum_qty,
            "sell_price":     round(self.sell_exp_price,2),
            "sell_date":      date,
            "min_max_days":   min_max_days,
            "profit":         round(cur_profit,2)
        }
        new_df = pd.DataFrame([new_data])
        self.df_stat = pd.concat([self.df_stat, new_df], ignore_index=True)

    def Op_xd(self, date, debug=0):
        if self.bonus_df.empty:
            return

        bonus = self.bonus_df[self.bonus_df["date"] == date]
        if len(bonus) <= 0:
            return

        if self.buy_count != 0: # 还未开始first_buy也无需除权
            # method1: XD the original value
            self.min_price_forsell = self.xd(self.min_price_forsell, bonus, debug)
            self.first_buy_price_fornext = self.xd(self.first_buy_price_fornext, bonus, debug)
            self.sell_exp_price = self.min_price_forsell * self.chg_perc
            self.next_buy_price = self.first_buy_price_fornext * (1-self.interval*self.buy_count)

            #增加profit
            cur_profit = float(bonus['bonus'].iloc[0]) * ( self.accum_qty / float(bonus['base'].iloc[0]))
            self.accum_profit += cur_profit

            if debug:
                print('    {} XD first/first_fornext/buy_count | min/min_forsell | next_buy/sell_exp {:.3f} {:.3f} {:.1f} | {:.3f} {:.3f} | {:.3f} x {} {:.3f}'.format(date,
                    self.first_buy_price, self.first_buy_price_fornext, self.buy_count,
                    self.min_price, self.min_price_forsell, 
                    self.next_buy_price, self.next_buy_qty, self.sell_exp_price))
                print('    {} XD profit {:.3f} x {:.3f} / {:.3f} = {:.3f}'.format(date, self.accum_qty, float(bonus['bonus'].iloc[0]), float(bonus['base'].iloc[0]), cur_profit))
        else:
            if debug:
                print(f'    {date} XD still no first buy')
            pass

    def Op(self, chg_perc, interval, start_date, end_date, debug=0):
        if self.df_allday.empty:
            print('df_allday empty')
            return None

        rt = RecTime()

        self.start_date = start_date
        self.end_date = end_date
        self.chg_perc = chg_perc
        self.interval = interval
        self.day_df = self.df_allday[(self.df_allday["date"] >= start_date) & (self.df_allday["date"] <= end_date)]
        if self.day_df.empty:
            print('day_df empty, no date match')
            return
        self.init_deal()

        # 遍历每一天
        if debug:
            print('date       low      high      open     close');
        for i, row in self.day_df.iterrows():
            date = str(row["date"])

            if debug:
                print('{} {:8.3f} {:8.3f}  {:8.3f} {:8.3f}'.format(date, row['low'], row['high'], row['open'], row['close']));

            # 判断是否存在除权的情况
            self.Op_xd(date, debug)

            # 当然价格可能：先低再高、先高再低
            # 策略：优先处理卖, 并且采用以前的min价格得到的sell_exp, 因此注释掉下面的代码; 当天只进行一种操作，要么买，要么卖
            # 然后考虑：第一次买入，更新min当天除权，
            #           第一次买入当天除权:    不参与除权
            #           当天最低最高价范围很大: 不是第一天，先对已有的min除权，先考虑卖出；第一天，只考虑买入
            # 更新最低价、卖出价

            # 判断是否卖出
            if self.buy_count != 0 and row["high"] >= self.sell_exp_price:
                cur_profit = self.sell_exp_price * self.accum_qty - self.accum_cost
                self.accum_profit += cur_profit
                if self.max_cost < self.accum_cost:
                    self.max_cost = self.accum_cost
                if debug:
                    print('    {} sell {:.2f} = {:.2f} * {:.1f} - {:.2f}'.format(date, cur_profit, self.sell_exp_price, self.accum_qty, self.accum_cost))

                self.push_stat(date, cur_profit)
                self.init_deal()
                continue

            # 判断是否止损卖出
            if self.buy_count >= 99 and row["low"] <= self.next_buy_price:
                self.sell_exp_price = row["low"] # 替换"期望卖出价格", 为了记录log
                cur_profit = self.sell_exp_price * self.accum_qty - self.accum_cost
                self.accum_profit += cur_profit
                if self.max_cost < self.accum_cost:
                    self.max_cost = self.accum_cost
                if debug:
                    print('    {} sell {:.2f} = {:.2f} * {:.1f} - {:.2f} stop lossing'.format(date, cur_profit, row["low"], self.accum_qty, self.accum_cost))

                self.push_stat(date, cur_profit)
                self.init_deal()
                continue

            # 判断是否买入
            while row["low"] <= self.next_buy_price:
                if self.buy_count == 0:
                    self.first_buy_price = (row['open'] + ((row["low"] + row["high"]) / 2)) /2 #low和high差距太大时，再和open做下平均
                    #self.first_buy_price = (row["low"] + row["high"]) / 2
                    self.first_buy_date = date

                    self.first_buy_price_fornext = self.first_buy_price
                    self.next_buy_price = self.first_buy_price_fornext
                if self.accum_qty == 0:
                    cost_each_before = np.nan
                else:
                    cost_each_before = self.accum_cost / self.accum_qty
                self.accum_cost += self.next_buy_price * self.next_buy_qty
                self.accum_qty += self.next_buy_qty
                self.buy_count += 1
                if debug:
                    cost_each_cur = self.accum_cost / self.accum_qty
                    cost_each_chg = (cost_each_before - cost_each_cur) / cost_each_before
                    print('    {} buy{} {:.3f} x {:.1f} = {:.1f} {:.1f}->{:.1f} {:.3f}->{:.3f} {:.1f}%'.format(date, 
                        self.buy_count, self.next_buy_price, self.next_buy_qty, self.next_buy_price*self.next_buy_qty,
                        self.accum_qty-self.next_buy_qty, self.accum_qty, cost_each_before, cost_each_cur, cost_each_chg*100.0))

                # 每次买入的预设价格：第1次买入价格 * (1-0.03*买入次数)，第1,2,3,4次买入价格为：97%,94%,91%,88%...
                self.next_buy_price = self.first_buy_price_fornext * (1-self.interval*self.buy_count)
                # 每次购买数量：2^购买次数, 第1，2，3，4次购买数量为：100,200,400,800,1600,3200
                self.next_buy_qty = np.round(np.exp2(self.buy_count/self.dec_buy_ratio))*100
        
            # 更新最低价、卖出价
            if self.buy_count != 0 and row["low"] < self.min_price_forsell:
                if debug:
                    print('    {} min {:.2f} {:.2f} -> {:.2f}'.format(date, self.min_price, self.min_price_forsell, row["low"]))
                # min_price不进行除权，min_price_forsell需要除权
                self.min_price = row["low"]
                self.min_price_forsell = self.min_price
                self.min_date = date
                self.sell_exp_price = self.min_price_forsell * self.chg_perc

        if self.buy_count != 0:
            self.push_stat(np.nan, np.nan)
            if self.max_cost < self.accum_cost:
                self.max_cost = self.accum_cost

        rt.show_ms()
        return self.df_stat

    def show_cur(self):
        if self.day_df.empty:
            print('day_df empty')
            return

        df_rows = self.day_df.loc[self.day_df['date'] <= self.end_date] # 确保是按照date排序的,找到最靠近end_date的一天计算当前收益
        if len(df_rows) == 0:
            print("Error: No latest day found.")
            print(self.day_df)
            return
        day = df_rows.iloc[-1]

        if self.df_stat.empty:
            print('{} no profit first day?'.format(self.ts_code))
            return

        last = self.df_stat.iloc[-1]
        unit_cost = last['accum_cost']/last['accum_qty']
        cur_profit = (day['high'] - unit_cost)*last['accum_qty']

        max_cost = self.df_stat['accum_cost'].max()
        norm_co = max_cost/1000000
        norm_cur_profit = cur_profit/norm_co

        print('                            profit_cur   {:7.0f} norm_cur     {:7.0f}'.format(cur_profit, norm_cur_profit), end=' ')
        if pd.isna(last['date']):
            print('hold_cur {:.2f} x {:.0f} ({} {}-{})'.format(
                unit_cost, last['accum_qty'], day['date'], day['low'], day['high']))

        doc = {
            "cur_profit":      int(cur_profit),
            "norm_cur_profit": int(norm_cur_profit),
            "cur_cost":        int(last['accum_cost'])
        }
        return doc

def show_stat(ts_code, start_date, end_date, chg_perc, interval, df_stat):
    max_cost = df_stat['accum_cost'].max()
    accum_profit = df_stat['profit'].sum()
    max_buy_count = df_stat['buy_count'].max()

    print('{} {}-{} {} {}'.format(ts_code, start_date, end_date, chg_perc, interval))

    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', None):
        print(df_stat.to_string(float_format="{:.1f}".format))

    norm_co = max_cost/1000000
    norm_accum_profit = accum_profit/norm_co

    print('----------')
    print('{} {}'.format(start_date, end_date), end=' ')
    print('{:9}'.format(ts_code), end=' ')
    print('profit_accum {:7.0f}'.format(accum_profit), end=' ')
    print('norm_accum   {:7.0f}'.format(norm_accum_profit), end=' ')
    print('max_cost     {:7.0f}'.format(max_cost), end=' ')
    print('max_buy_count {}'.format(max_buy_count), end=' ')

    print()

    #对(self.df_stat)进行一个总结: 去除date是NaN的行数,即卖出次数, min_max_days的平均
    sell_counts = df_stat['date'].count()
    avg_mm_days = df_stat['min_max_days'][df_stat['date'].notna()].mean()

    # 处理 avg_mm_days
    if np.isnan(avg_mm_days):
        avg_mm_days_value = None  # 或者设置为您需要的默认值，如 0
    else:
        avg_mm_days_value = int(round(avg_mm_days, 2))

    summary_dict = {
        "ts_code":    ts_code,
        "profit_accum":      int(round(accum_profit,0)),
        "profit_accum_norm": int(round(norm_accum_profit,0)),
        "max_cost":          int(round(max_cost,0)),
        "max_buy_count":     int(max_buy_count),
        "sell_counts":       int(sell_counts),
        "avg_mm_days":       avg_mm_days_value
    }
    return summary_dict

if __name__ == '__main__':
    if len(sys.argv) == 5: 
        ts_code    = sys.argv[1]
        start_date = str(sys.argv[2])
        end_date   = str(sys.argv[3])
        chg_perc   = float(sys.argv[4])

        # 获取code: name, industry
        client = MongoClient('mongodb://localhost:27017/')
        db = client['stk1']
        collection = db['basic']
        pattern = '^' + re.escape(ts_code)
        regex = re.compile(pattern)
        docs = collection.find( { 'ts_code': regex }, { '_id': 0, 'ts_code': 1, 'name': 1, 'industry': 1 })
        data_list = [{'code': doc.get('ts_code'), 'name': doc.get('name'), 'industry': doc.get('industry')} for doc in docs]
        for item in data_list:
            print(item)

        interval   = 0.03
        so = StockOp(ts_code)
        df_stat = so.Op(chg_perc, interval=interval, start_date=start_date, end_date=end_date, debug=0)
        show_stat(ts_code, start_date, end_date, chg_perc, interval, df_stat)
        so.show_cur()
    else:
        print('./StockOp.py ts_code start_date end_date chg_perc')
        print('./StockOp.py 002475 20201013 20250331 1.55 # 价格最高点')

