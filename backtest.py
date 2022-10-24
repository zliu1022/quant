#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint

import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

import random
from time import time

from datetime import datetime
from datetime import timedelta

from StockQuery import StockQuery

class BackTest:
    def init(self):
        client = MongoClient(port=27017)
        db = client.stk1
        self.col_bonus = db.bonus
        self.col_day = db.day

        self.ts_code = ''
        '''
        [
            {'cost': 10, 'qty': 1},
            {'cost':  8, 'qty': 2},
            {'cost':  4, 'qty': 8}
        ]
        '''
        self.bonus = []
        self.day = []
        self.date_list = []
        self.low_list = []
        self.high_list = []
        self.date_arr = np.array(self.date_list)
        self.low_arr = np.array(self.low_list)
        self.high_arr = np.array(self.high_list)

        self.hold = []
        self.cash = 0.0
        self.ori_cash = 0.0
        self.total_cost = 0.0
        self.total_qty = 0
        self.mkt_cost = 0.0 # total_qty * close_price
        self.max_cost = 0.0

        self.df_hold = pd.DataFrame()

    def __init__(self, ts_code):
        self.init()
        self.set_code(ts_code)

    def clear_hold(self):
        self.hold = []
        self.cash = 0.0
        self.total_cost = 0.0
        self.total_qty = 0
        self.mkt_cost = 0.0 # total_qty * close_price
        self.max_cost = 0.0

    def set_code(self, ts_code):
        self.ts_code = ts_code
        v = {'ts_code': ts_code}

        ref = self.col_bonus.find_one(v)
        if ref != None:
            self.bonus = ref['items']
            print('Got bonus', type(self.bonus))
            print(self.bonus[0]['date'], self.bonus[0]['plan_explain'])
        else:
            print('Error, no bonus', ts_code)

        ref = self.col_day.find_one(v)
        if ref != None:
            self.day = ref['day']
            print('Got day line', len(self.day), type(self.day))
            print(self.day[0]['date'], self.day[0]['open'])

            # change sequence index 0 is old
            self.day = self.day[::-1]

            self.date_list = []
            self.low_list = []
            self.high_list = []
            for x in self.day:
                self.date_list.append(x['date'])
                self.low_list.append(x['low'])
                self.high_list.append(x['high'])

            self.date_arr = np.array(self.date_list)
            self.low_arr = np.array(self.low_list)
            self.high_arr = np.array(self.high_list)
        else:
            print('Error, no day line', ts_code)

        print()

    # random for:
    # idle, buy, sell is random and mutually exclusive
    # buy qty is random between 10,20,30,40,50
    # buy price is random between low and high
    # sell price is random between low and high
    # sell qty is latest buy
    def strategy_random(self, day):
        choice = random.randint(0, 2)
        if choice == 0:
            print('do nothing          ', end='')
        elif choice == 1:
            # buy strategy
            qty = random.randint(1, 5) * 10
            cost = round(random.uniform(day['low'], day['high']),2)
            self.push({'cost':cost, 'qty':qty})
            print('buy  {:3d} with {:.2f}'.format(qty, cost), end=' ')
        else:
            # sell strategy
            cost = round(random.uniform(day['low'], day['high']),2)
            last = self.pop(cost)
            if last != None:
                qty = last['qty']
                print('sell {:3d} with {:.2f}'.format(qty, cost), end=' ')
            else:
              print('nothing to sell     ', end='')

    def bonus_update_hold(self, bonus_date):
        bonus = self.get_bonus(bonus_date)
        if bonus == None:
            return

        base = float(bonus['base'])
        free = float(bonus['free'])
        new  = float(bonus['new'])
        dividend = float(bonus['bonus'])

        pos = bonus['plan_explain'].find('(')
        if pos != -1:
            bonus_str = bonus['plan_explain'][0:pos]
        else:
            bonus_str = bonus['plan_explain']

        print('{} {} cash {:8.2f} total_qty {:8.2f} -> '.format(bonus_date, bonus_str, self.cash, self.total_qty), end='')
        self.cash      += self.total_qty / base * dividend
        self.total_qty += self.total_qty / base * (free + new)
        print('cash {:8.2f} total_qty {:8.2f}'.format(self.cash, self.total_qty))
        return

    def run(self, start_date, end_date):
        s_time = time()

        # start_date as random
        #random_day = int(random.uniform(0,7))
        #start_date = datetime.strftime(datetime.strptime(start_date, '%Y%m%d')+timedelta(days=random_day), '%Y%m%d')

        for x in self.day:
            if x['date'] <= end_date and x['date'] >= start_date:
                self.bonus_update_hold(x['date'])

                print('%s %.2f %.2f' % (x['date'], x['low'], x['high']), end=' ')
                # strategy
                # input:  date,low,high,bonus
                # update: hold[], cash, total_cost, total_qty
                # op:     push pop
                self.strategy_random(x)
                self.mkt_cost = self.total_qty * x['close']
                self.show()

        e_time = time()
        print('cost %.2f s' % (e_time - s_time))

    def get_bonus(self, date):
        for x in self.bonus:
            if x['date'] == date:
                return x
        return None

    def set_cash(self, cash):
        self.cash = cash
        self.ori_cash = cash

    def push(self, cost_qty):
        self.hold.append(cost_qty)
        self.cash       -= round(cost_qty['cost'] * cost_qty['qty'], 2)
        self.total_qty  += cost_qty['qty']
        self.total_cost += round(cost_qty['cost'] * cost_qty['qty'], 2)
        if self.total_cost > self.max_cost:
            self.max_cost = self.total_cost

    def pop(self, cost):
        if len(self.hold) == 0:
            return None
        ori = self.hold.pop()
        self.cash       += cost * ori['qty']
        self.total_qty  -= ori['qty']
        self.total_cost -= round(ori['cost'] * ori['qty'], 2)
        return ori

    def push_df(self, cost_qty):
        df_buy = pd.DataFrame([cost_qty])
        self.df_hold = pd.concat(self.df_hold, df_buy).reset_index(drop=True)
        self.cash       -= round(cost_qty['cost'] * cost_qty['qty'], 2)
        self.total_qty  += cost_qty['qty']
        self.total_cost += round(cost_qty['cost'] * cost_qty['qty'], 2)
        if self.total_cost > self.max_cost:
            self.max_cost = self.total_cost

    def pop_df(self):
        if len(self.df_hold.index) == 0:
            return None
        self.df_hold = self.df_hold.drop([0]).reset_index(drop=True)
        self.cash       += cost * ori['qty']
        self.total_qty  -= ori['qty']
        self.total_cost -= round(ori['cost'] * ori['qty'], 2)
        return ori

    def buy(self, cost_qty):
        if (self.cash - cost_qty['cost'] * cost_qty['qty']) < 0:
            #print('Error cash not enough')
            qty = int(self.cash / cost_qty['cost'])
        else:
            qty = cost_qty['qty']
        self.total_qty += qty
        self.total_cost += cost_qty['cost'] * qty
        self.cash -= cost_qty['cost'] * qty
        return {'cost': cost_qty['cost'], 'qty': qty}

    def sell(self, cost_qty):
        if (self.total_qty - cost_qty['qty']) < 0:
            #print('Error sell no hold')
            self.total_cost -= cost_qty['cost'] * self.total_qty
            self.cash += cost_qty['cost'] * self.total_qty
            self.total_qty = 0
        else:
            self.total_cost -= cost_qty['cost'] * cost_qty['qty']
            self.cash += cost_qty['cost'] * cost_qty['qty']
            self.total_qty -= cost_qty['qty']

    def show(self):
        print('cash {:8.2f} total_qty {:7.2f} total_cost {:7.2f}({:7.2f}) mkt_cost {:7.2f} benefit {:7.2f}'.format(
            self.cash, self.total_qty, 
            self.total_cost, self.max_cost, self.mkt_cost, 
            self.cash + self.mkt_cost - self.ori_cash ))
        pprint(self.hold)
        print()

    def test(self, start_date, end_date):
        for x in ref['items']:
            if x['date'] <= end_date and x['date'] >= start_date:
                print(x['date'], x['base'], x['free'], x['new'], x['bonus'], x['plan_explain'])
        for x in ref['day']:
            if x['date'] <= end_date and x['date'] >= start_date:
                print(x['date'], x['open'], x['close'])

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        ts_code    = '002475.SZ'
        start_date = '20220601'
        end_date   = '20220801'
    elif len(sys.argv) == 4:
        ts_code    = sys.argv[1]
        start_date = sys.argv[2]
        end_date   = sys.argv[3]
    else:
        print('./BackTest.py 002475.SZ 20220101 20220115')
        quit()

    sq = StockQuery()
    ret = sq.check_bad_bonus(ts_code)
    if ret != 0:
        print('bad_bonus')
        quit()

    bt = BackTest(ts_code)
    bt.run(start_date, end_date)

