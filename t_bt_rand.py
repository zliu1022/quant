#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from pprint import pprint

import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

import random
from time import time

class BackTest:
    def __init__(self):
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

    def strategy_random(self, day):
        choice = random.randint(0, 2)
        if choice == 0:
            print('do nothing          ', end='')
        elif choice == 1:
            qty = random.randint(1, 5) * 10
            cost = round(random.uniform(day['low'], day['high']),2)
            self.push({'cost':cost, 'qty':qty})
            print('buy  %3d with %.2f ' % (qty, cost), end=' ')
        else:
            cost = round(random.uniform(day['low'], day['high']),2)
            last = self.pop(cost)
            if last != None:
                qty = last['qty']
                print('sell %3d with %.2f' % (qty, cost), end=' ')
            else:
                print('nothing to sell  ', end='')

    def bonus_update(self, x):
        bonus = self.get_bonus(x['date'])
        if bonus != None:
            pos = bonus['plan_explain'].find('(')
            if pos != -1:
                bonus_str = bonus['plan_explain'][0:pos]
            else:
                bonus_str = bonus['plan_explain']
            print(bonus_str, end=' ')

            # update hold
            base = float(bonus['base'])
            free = float(bonus['free'])
            new  = float(bonus['new'])
            bonus = float(bonus['bonus'])
            self.cash += self.total_qty / base * bonus
            self.total_qty += self.total_qty / base * (free + new)

            # update expect buy&sell

    def run(self, start_date, end_date):
        for x in self.day:
            if x['date'] <= end_date and x['date'] >= start_date:
                print('%s %.2f %.2f' % (x['date'], x['low'], x['high']), end=' ')

                self.bonus_update(x)

                # strategy
                # input:  date,low,high,bonus
                # update: hold[], cash, total_cost, total_qty
                # op:     push pop
                self.strategy_random(x)
                self.mkt_cost = self.total_qty * x['close']
                self.show()

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
        self.cash -= round(cost_qty['cost'] * cost_qty['qty'], 2)
        self.total_qty += cost_qty['qty']
        self.total_cost += round(cost_qty['cost'] * cost_qty['qty'], 2)
        if self.total_cost > self.max_cost:
            self.max_cost = self.total_cost

    def pop(self, cost):
        if len(self.hold) == 0:
            #print('Error pop no hold')
            return None
        ori = self.hold.pop()
        self.cash += cost * ori['qty']
        self.total_qty -= ori['qty']
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
        print('cash %.2f total_qty %3d total_cost %.2f(%.2f) mkt_cost %.2f benefit %.2f' 
            % (self.cash, self.total_qty, 
            self.total_cost, self.max_cost, self.mkt_cost, 
            self.cash + self.mkt_cost - self.ori_cash ))

    def test(self, start_date, end_date):
        for x in ref['items']:
            if x['date'] <= end_date and x['date'] >= start_date:
                print(x['date'], x['base'], x['free'], x['new'], x['bonus'], x['plan_explain'])
        for x in ref['day']:
            if x['date'] <= end_date and x['date'] >= start_date:
                print(x['date'], x['open'], x['close'])

if __name__ == '__main__':
    ts_code = '603005.SH'

    s_time = time()
    bt = BackTest()
    bt.set_code(ts_code)
    e_time = time()
    print('BackTest cost %.2f s' % (e_time - s_time))

    # review dayline and show bonus
    start_date = '20220501'
    end_date = '20220531'
    run_num = 10

    rev = 0.0 #revenue
    rev_list = []
    rev_ratio = 0.0
    rev_ratio_list = []

    s_time = time()
    for _ in range(0, run_num):
        bt.clear_hold()
        bt.set_cash(10000)
        bt.run(start_date, end_date)

        rev = bt.cash + bt.mkt_cost - bt.ori_cash
        rev_ratio = (bt.mkt_cost-bt.total_cost) / bt.max_cost
        rev_list.append(rev)
        rev_ratio_list.append(rev_ratio)
        print()
    e_time = time()
    print('Run cost %.2f s each cost %.2f s' % ( (e_time - s_time), (e_time - s_time)/float(run_num)))

    rev_arr = np.array(rev_list)
    print('avg %.2f' % np.average(rev_arr))
    print('mean %.2f' % np.mean(rev_arr))
    print('std %.2f' % np.std(rev_arr))
    print('var %.2f' % np.var(rev_arr))
    print()

    rev_ratio_arr = np.array(rev_ratio_list)
    print('avg %.1f%%'  % (100.0*np.average(rev_ratio_arr)))
    print('mean %.1f%%' % (np.mean(rev_ratio_arr)*100.0))
    print('std %.1f%%'  % (np.std(rev_ratio_arr)*100.0))
    print('var %.1f%%'  % (np.var(rev_ratio_arr)*100.0))
    print()
