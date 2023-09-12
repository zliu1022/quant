#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import pandas as pd
import numpy as np
from StockQuery import StockQuery
from Utils import RecTime
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class StockOpInv:
    def __init__(self):
        return

    def set(self, i, chg_perc, interval, start_date, end_date):
        if isinstance(i, str):
            self.ts_code = i
            self.name = ''
            self.industry = 'None'
        elif isinstance(i, dict):
            self.ts_code = i['ts_code']
            self.name = i['name']
            self.industry = i['industry']
            if self.industry == None:
                self.industry = 'None'
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

        '''
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', -1):
            print(df_day)
        print()
        '''

        self.day_df = pd.DataFrame()
        self.bonus_df = pd.DataFrame()
        if df_day.empty:
            return
        self.day_df = df_day[(df_day["date"] >= start_date) & (df_day["date"] <= end_date)]
        self.bonus_df = df_bonus

        d_first = df_day.iloc[0]
        d_end = df_day.iloc[-1]

        if d_end['turnoverrate'] != 0:
            mv = d_end['volume']/(d_end['turnoverrate']/100) * d_end['close']
        else:
            mv = 0
        self.mv = round(mv/100000000,2)

        if d_first['turnoverrate'] != 0:
            mv_ori = d_first['volume']/(d_first['turnoverrate']/100) * d_first['close']
        else:
            mv_ori = 0
        self.mv_ori = round(mv_ori/100000000,2)

        df_bd = sq.query_bd_tscode(self.ts_code.split('.')[0])
        self.pe = 0
        if not df_bd.empty:
            self.pe = df_bd.iloc[0]['市盈率']

    '''
    def __del__(self):
        if self.day_df is not None:
            del self.day_df
        if self.bonus_df is not None:
            del self.bonus_df
    '''

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
        base = float(xd["base"])
        bonus = float(xd['bonus'])
        free = float(xd['free'])
        new = float(xd['new'])
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

        self.df_stat = self.df_stat.append(
            {"date": date, 
            "first_buy_price": round(self.first_buy_price,2),
            "first_buy_date": self.first_buy_date,
            "min_price": round(self.min_price,2),
            "min_date": self.min_date,
            "buy_count": self.buy_count,
            "accum_cost": round(self.accum_cost,2),
            "accum_qty": self.accum_qty,
            "sell_price": round(self.sell_exp_price,2),
            "sell_date": date,
            "min_max_days":min_max_days,
            "profit": round(cur_profit,2)}, 
            ignore_index=True)

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
            self.accum_profit += float(xd['bonus']) * ( self.accum_qty / float(xd['base']))

            # method2: XD the current value
            # 这个逻辑有矛盾，虽然这次next_buy进行了除权
            # 但下一次买时，next_buy会按照first_buy计算，和这次XD完全无关了，肯定没道理
            '''
            self.sell_exp_price = self.xd(self.sell_exp_price, bonus)
            self.next_buy_price = self.xd(self.next_buy_price, bonus)
            '''

            if debug:
                print('    {} XD first/first_fornext/min/min_forsell/next/sell {:.3f} {:.3f} {:.3f} {:.3f} {:.3f}({}) {:.3f}'.format(date,
                    self.first_buy_price, self.first_buy_price_fornext, self.min_price, self.min_price_forsell, self.next_buy_price, self.next_buy_qty, self.sell_exp_price))
        else:
            if debug:
                print(f'    {date} XD still no first buy')
            pass

    def Op(self, i, chg_perc, interval, start_date, end_date, debug=0):
        self.set(i, chg_perc, interval, start_date, end_date)

        if self.day_df.empty:
            return

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

            # 判断是否买入
            while row["low"] <= self.next_buy_price:
                if self.buy_count == 0:
                    self.first_buy_price = (row['open'] + ((row["low"] + row["high"]) / 2)) /2 #low和high差距太大时，再和open做下平均
                    #self.first_buy_price = (row["low"] + row["high"]) / 2
                    self.first_buy_date = date

                    self.first_buy_price_fornext = self.first_buy_price
                    self.next_buy_price = self.first_buy_price_fornext
                self.accum_cost += self.next_buy_price * self.next_buy_qty
                self.accum_qty += self.next_buy_qty
                self.buy_count += 1
                if debug:
                    print('    {} buy{} {:.3f} x {:.1f} = {:.1f}'.format(date, self.buy_count, self.next_buy_price, self.next_buy_qty, self.next_buy_price*self.next_buy_qty))

                self.next_buy_price = self.first_buy_price_fornext * (1-self.interval*self.buy_count)
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

    # 先卖再买
    def Op_inv(self, i, chg_perc, interval, start_date, end_date, debug=0):
        self.set(i, chg_perc, interval, start_date, end_date)

        if self.day_df.empty:
            return

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

            # 判断是否卖出 -> 买入
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

            # 判断是否买入 -> 卖出
            while row["low"] <= self.next_buy_price:
                if self.buy_count == 0:
                    self.first_buy_price = (row['open'] + ((row["low"] + row["high"]) / 2)) /2 #low和high差距太大时，再和open做下平均
                    #self.first_buy_price = (row["low"] + row["high"]) / 2
                    self.first_buy_date = date

                    self.first_buy_price_fornext = self.first_buy_price
                    self.next_buy_price = self.first_buy_price_fornext
                self.accum_cost += self.next_buy_price * self.next_buy_qty
                self.accum_qty += self.next_buy_qty
                self.buy_count += 1
                if debug:
                    print('    {} buy{} {:.3f} x {:.1f} = {:.1f}'.format(date, self.buy_count, self.next_buy_price, self.next_buy_qty, self.next_buy_price*self.next_buy_qty))

                self.next_buy_price = self.first_buy_price_fornext * (1-self.interval*self.buy_count)
                self.next_buy_qty = np.round(np.exp2(self.buy_count/self.dec_buy_ratio))*100
        
            # 更新最低价、卖出价 -> 最高价、买入价
            if self.buy_count != 0 and row["low"] < self.min_price_forsell:
                if debug:
                    print('    {} min {:.2f} {:.2f} -> {:.2f}'.format(date, self.min_price, self.min_price_forsell, row["low"]))
                # min_price不进行除权，min_price_forsell需要除权
                self.min_price = row["low"]
                self.min_price_forsell = self.min_price
                self.min_date = date
                self.sell_exp_price = self.min_price_forsell * self.chg_perc
            if self.sell_count != 0 and row["low"] > self.max_price_forbuy:
                if debug:
                    print('    {} max {:.2f} {:.2f} -> {:.2f}'.format(date, self.max_price, self.max_price_forbuy, row["high"]))
                # max_price不进行除权，max_price_forbuy需要除权
                self.max_price = row["high"]
                self.max_price_forbuy = self.max_price
                self.max_date = date
                self.buy_exp_price = self.max_price_forbuy / self.chg_perc

        if self.buy_count != 0:
            self.push_stat(np.nan, np.nan)
            if self.max_cost < self.accum_cost:
                self.max_cost = self.accum_cost

        if self.sell_count != 0:
            self.push_stat_inv(np.nan, np.nan)
            if self.max_debt < self.accum_debt:
                self.max_debt = self.accum_debt

    def show_stat(self):
        print('{} {}-{} {} {}'.format(self.ts_code, self.start_date, self.end_date, self.chg_perc, self.interval))
        if self.day_df.empty:
            print('day_df empty')
            print()
            return
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', -1):
            print(self.df_stat)

        '''
        today_df = self.day_df[self.day_df["date"] == self.end_date]
        if today_df.empty:
            print(self.day_df)
            return
        '''
        df_rows = self.day_df.loc[self.day_df['date'] <= self.end_date] # 确保是按照date排序的,找到最靠近end_date的一天计算当前收益
        if len(df_rows) == 0:
            print("Error: No latest day found.")
            print(self.day_df)
            return
        day = df_rows.iloc[-1]

        if self.df_stat.empty:
            print('{} {} {:.0f} {} no profit first day?'.format(self.ts_code, self.name, self.mv, self.pe))
            return

        last = self.df_stat.iloc[-1]
        unit_cost = last['accum_cost']/last['accum_qty']
        cur_profit = (day['high'] - unit_cost)*last['accum_qty']

        norm_co = self.max_cost/1000000
        norm_accum_profit = self.accum_profit/norm_co
        norm_cur_profit = cur_profit/norm_co

        # date code name industry mv(mv_ori) pe profit(accum cur) norm_profit(accum cur) max_cost
        print('{} {}'.format(self.start_date, self.end_date), end=' ')
        print('{:9} {:8} {:8} {:7.1f}({:7.1f}) {}'.format(self.ts_code, self.name, self.industry, self.mv, self.mv_ori, self.pe), end=' ')
        print('profit {:7.0f} {:7.0f}'.format(self.accum_profit, cur_profit), end=' ')
        print('norm {:7.0f} {:7.0f}'.format(norm_accum_profit, norm_cur_profit), end=' ')
        print('max_cost {:7.0f}'.format(self.max_cost), end=' ')

        if pd.isna(last['date']):
            print('hold {:.2f}*{:.0f}({}-{})'.format(
                unit_cost, last['accum_qty'], day['low'], day['high']))
        print()

        #对(self.df_stat)进行一个总结: 去除date是NaN的行数,即卖出次数, min_max_days的平均
        sell_counts = self.df_stat['date'].count()
        avg_mm_days = self.df_stat['min_max_days'][self.df_stat['date'].notna()].mean()

        summary_dict = {
            "start_date": self.start_date,
            "end_date":   self.end_date,
            "ts_code":    self.ts_code,
            "name":       self.name,
            "industry":   self.industry,
            "mv":         self.mv,
            "mv_ori":     self.mv_ori,
            "pe":         self.pe,
            "profit_accum": round(self.accum_profit,2),
            "profit_cur":  round(cur_profit,2),
            "norm_accum_profit": round(norm_accum_profit,2),
            "norm_cur_profit": round(norm_cur_profit,2),
            "max_cost": round(self.max_cost,2),
            "sell_counts": sell_counts,
            "avg_mm_days": round(avg_mm_days,2)
        }
        return summary_dict

    def op_month(self, start_date, end_date):
        start_d = datetime.strptime(start_date, '%Y%m%d')
        end_d   = datetime.strptime(end_date,   '%Y%m%d')
        for i in range(end_d.month - start_d.month + (end_d.year - start_d.year) * 12):
            new_d = start_d + relativedelta(months=i)
            new_date = datetime.strftime(new_d, '%Y%m%d')
            print('{} - {} {} days'.format(new_date, end_date, (end_d-new_d).days))

    def op_days(self, start_date, end_date, start_interval, interval):
        d = []
        start_d = datetime.strptime(start_date, '%Y%m%d')
        end_d   = datetime.strptime(end_date,   '%Y%m%d')
        n = start_interval
        m = interval
        while True:
            new_end_d = start_d + timedelta(days=m)
            '''
            # 确保产生的时段都有interval的天数
            if new_end_d > end_d:
                break
            '''
            start_str = start_d.strftime("%Y%m%d")
            end_str = new_end_d.strftime("%Y%m%d")
            #print(start_str, end_str, (new_end_d-start_d).days)
            d.append({'start_date':start_str, 'end_date':end_str})
            start_d += timedelta(days=n)
            if start_d >= end_d:
                break
        return d

def t_1code(sq, so):
    ts_code    = '002475.SZ'
    #ts_code    = '600519.SH' # 茅台
    #ts_code    = '002273.SZ' # 水晶
    #ts_code    = '000425.SZ' # 徐工
    so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230901", debug=1)

    #ts_code = "830946.BJ" # 在20210624-20220321 出现6次卖，norm盈利440675,11743
    #so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date="20210624", end_date="20220321", debug=1)
    so.show_stat()

    rt.show_s()
    quit()

    ts_code = '002456.SZ' # 欧菲光
    ts_code = '300476.SZ'

    ts_code = '831726' # 朱老六，20200818这天波动很大14~31
    #so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230728")
    #so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date="20200310", end_date="20200906")
    #so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date="20200818", end_date="20200906")
    #so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date="20200818", end_date="20200923")
    #so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date="20210624", end_date="20230728")

    #ts_code = '002050.SZ' #逐步对照过
    #so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date="20200708", end_date="20220610")

    #ts_code = '002475.SZ'
    #so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date="20200101", end_date="20230728")

    #so.show_stat()

    ts_code = '831726' # 朱老六，前复权后初始股价为负值
    ts_code = '000670' # 盈方微型，20200101-20230316出现很多块day数据为空
    ts_code = '002475.SZ'
    #date_list = so.op_days(start_date="20200101", end_date="20230728", start_interval=180, interval=270)
    date_list = so.op_days(start_date="20211101", end_date="20230829", start_interval=10, interval=800)
    for _,d in enumerate(date_list):
        so.Op(ts_code, chg_perc=1.55, interval=0.03, start_date=d['start_date'], end_date=d['end_date'])
        so.show_stat()

    rt.show_s()
    quit()

def t_codes(sq, so):
    code_list = [ # 未知列表
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
    code_list = [ # industry 铅锌
        '000060.SZ',
        '600497.SH',
        '000751.SZ',
        '000426.SZ',
        '000603.SZ',
        '600531.SH',
        '600961.SH',
        '000758.SZ',
        '600338.SH',
        '000688.SZ',
        '601020.SH'
    ]
    code_list = [ # industry 轻工机械
        '002611.SZ',
        '002444.SZ',
        '300195.SZ',
        '300173.SZ'
    ]
    code_list = [ # industry 化工机械
        '002698.SZ',
        '000852.SZ',
        '300228.SZ',
        '002430.SZ',
        '002337.SZ',
        '002353.SZ'
    ]
    code_list = [ # industry 旅游景点
        '002033.SZ',
        '603199.SH',
        '600706.SH',
        '600054.SH',
        '600593.SH',
        '000888.SZ',
        '300144.SZ',
        '603136.SH'
    ]
    code_list = [ # industry 铅锌,旅游景点,轻工机械,化工机械,四个industry，按照norm_cur_profit排序，全部是盈利的前17个
        '000060.SZ', #  中金岭南	铅锌
        '002698.SZ', #  博实股份	化工机械
        '002033.SZ', #	丽江股份	旅游景点
        '600497.SH', #	驰宏锌锗	铅锌
        '000852.SZ', #	石化机械	化工机械
        '000751.SZ', #	锌业股份	铅锌
        '002611.SZ', #	东方精工	轻工机械
        '603199.SH', #	九华旅游	旅游景点
        '002444.SZ', #	巨星科技	轻工机械
        '300228.SZ', #	富瑞特装	化工机械
        '600706.SH', #	曲江文旅	旅游景点
        '600054.SH', #	黄山旅游	旅游景点
        '000426.SZ', #	兴业银锡	铅锌
        '300195.SZ', #	长荣股份	轻工机械
        '000603.SZ', #	盛达资源	铅锌
        '600531.SH', #	豫光金铅	铅锌
        '600961.SH'  #	株冶集团	铅锌
    ]
    code_list = [
        '000670'
    ]
    date_list = so.op_days(start_date="20200101", end_date="20230728", start_interval=180, interval=270)
    for item in code_list:
        for i,d in enumerate(date_list):
            so.Op(item, chg_perc=1.55, interval=0.03, start_date=d['start_date'], end_date=d['end_date'])
            summary = so.show_stat()
    rt.show_s()
    quit()

def t_all(sq, so):
    df_all = pd.DataFrame()
    code_list = sq.query_basic(None)

    # 一旦出现异常，可以恢复到异常发生时的代码继续
    stock_codes = [item['ts_code'] for item in code_list]
    #start_code = '688627.SH'
    #start_index = stock_codes.index(start_code)
    start_index = 0

    date_list = so.op_days(start_date="20200101", end_date="20230728", start_interval=180, interval=270)
    for i in range(start_index, len(code_list)):
        for _,d in enumerate(date_list):
            so.Op(code_list[i], chg_perc=1.55, interval=0.03, start_date=d['start_date'], end_date=d['end_date'])
            summary = so.show_stat()
            df_all = df_all.append(summary, ignore_index=True)

    start_date="20200101"
    df_filename = "mv" + "-" + "all-" + start_date + "-op_days.csv"
    df_all.to_csv(df_filename, index=False)
    rt.show_s()
    quit()

def t_mv(sq, so):
    df_all = pd.DataFrame()

    if len(sys.argv) == 3:
        start_date = sys.argv[1]
        end_date   = sys.argv[2]
    else:
        start_date = "20200101"

    #v1 = 100; v2 = 5000
    #v1 = 30; v2 = 300
    v1 = 0; v2 = np.inf # 市值超过万亿的：中国石油，贵州茅台，工商银行，其中工商银行基本不波动，没有盈利空间
    code_list = sq.query_mktvalue(start_date, v1, v2)

    #stock_codes = [item['ts_code'] for item in code_list]
    #start_index = stock_codes.index('601577.SH')
    start_index = 0
    date_list = so.op_days(start_date="20200101", end_date="20230728", start_interval=180, interval=270)
    for i in range(start_index, len(code_list)):
        for _,d in enumerate(date_list):
            so.Op(code_list[i], chg_perc=1.55, interval=0.03, start_date=d['start_date'], end_date=d['end_date'])
            summary = so.show_stat()
            df_all = df_all.append(summary, ignore_index=True)

    start_date="20200101"
    df_filename = "mv" + str(v1) + "-" + str(v2) + "-" + start_date + "-op_days.csv"
    df_all.to_csv(df_filename, index=False)
    rt.show_s()
    quit()

if __name__ == '__main__':
    rt = RecTime()
    sq = StockQuery()
    so = StockOpInv()

    # 一个code
    t_1code(sq, so)

    # 固定列表
    #t_codes(sq, so)

    # 查询
    #t_all(sq, so)

    # 采用mktvalue进行筛选
    #t_mv(sq, so)

