#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import pandas as pd

class StockOp:
    def __init__(self, ts_code, chg_perc, interval, max_cost, start_date, end_date):
        # 连接到 MongoDB
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["stk1"]

        # 获取日线数据和分红除权数据
        self.day_data = db["day"].find_one({"ts_code": ts_code})["day"]
        self.bonus_data = db["bonus"].find_one({"ts_code": ts_code})["items"]

        # 将数据转化为 DataFrame
        #self.day_df = pd.DataFrame(self.day_data)
        self.day_df = pd.DataFrame(self.day_data)[::-1].reset_index(drop=True)
        self.bonus_df = pd.DataFrame(self.bonus_data)

        self.day_df = self.day_df[(self.day_df["date"] >= start_date) & (self.day_df["date"] <= end_date)]

        # 设置初始参数
        self.min_price = 9999.0
        self.sell_exp_price = 0.0
        self.first_buy_price = 0.0
        self.next_buy_price = 9999.0
        self.next_buy_qty = 100
        self.chg_perc = chg_perc
        self.interval = interval

        self.accum_profit = 0.0
        self.accum_cost = 0.0
        self.accum_qty = 0
        self.max_cost = max_cost

        self.buy_count = 0
        self.df_stat = pd.DataFrame()

    def xd(self, ori_p, xd):
        date = str(xd["date"])
        base = float(xd["base"])
        bonus = float(xd['bonus'])
        free = float(xd['free'])
        new = float(xd['new'])
        new_p = (ori_p * base)/(base+free+new)
        print('xd {} -> {} {} {} {} {} {}'.format(ori_p, new_p, date, base, bonus, free, new))
        return new_p
        
    def process_day(self):
        # 遍历每一天
        for i, row in self.day_df.iterrows():
            date = row["date"]

            # 判断是否存在除权的情况
            bonus = self.bonus_df[self.bonus_df["date"] == date]
            if len(bonus) > 0:
                print(bonus)
                print()
                self.min_price = self.xd(self.min_price, bonus)
                self.first_buy_price = self.xd(self.first_buy_price, bonus)

                self.sell_exp_price = self.min_price * self.chg_perc
                self.next_buy_price = self.first_buy_price * (1-self.interval*self.buy_count)
                print('xd min {:.2f} first_buy_p {:.2f} next_buy_price {:.2f} {} sell_exp_p {:.2f}'.format(self.min_price, self.first_buy_price, self.next_buy_price, self.next_buy_qty, self.sell_exp_price))

            if row["low"] < self.min_price:
                self.min_price = row["low"]
                self.sell_exp_price = self.min_price * self.chg_perc

            # 判断是否卖出
            if row["high"] >= self.sell_exp_price:
                cur_profit = self.sell_exp_price * self.accum_qty - self.accum_cost
                print('sell profit {}'.format(cur_profit))
                self.accum_profit += cur_profit
                self.accum_cost = 0
                self.buy_count = 0
                self.accum_qty = 0
                self.min_price = 9999.0
                self.first_buy_price = 0.0
                self.df_stat = self.df_stat.append({"date": date, "profit": cur_profit}, ignore_index=True)

            # 判断是否买入
            while row["low"] <= self.next_buy_price:
                if self.next_buy_price == 9999.0:
                    self.first_buy_price = (row["low"] + row["high"]) / 2
                    self.next_buy_price = self.first_buy_price
                self.buy_count += 1
                self.accum_cost += self.next_buy_price * self.next_buy_qty
                self.accum_qty += self.next_buy_qty
                print('buy {} {} {:.2f} {}'.format(date, self.buy_count, self.next_buy_price, self.next_buy_qty))

                self.next_buy_price = self.first_buy_price * (1-self.interval*self.buy_count)

    def get_stat(self):
        return self.df_stat

if __name__ == '__main__':
    stock_op = StockOp("002050.SZ", chg_perc=1.55, interval=0.03, max_cost=0, start_date="20200708", end_date="20220610")
    stock_op.process_day()
    df_stat = stock_op.get_stat()
    print(df_stat)


