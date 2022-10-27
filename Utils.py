#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy  as np

def create_buy_table(interval=0.025, inc_perc=1.1, dec_buy_ratio=5):
    num = round(1/interval) + 1

    a = pd.DataFrame({'dec_perc':np.arange(num)*interval})
    a.insert(1, 'cur_price',   (1-a.dec_perc)*100)
    a.insert(2, 'buy_qty',     np.round(np.exp2(np.arange(num)/dec_buy_ratio))*100)
    a.insert(3, 'acum_qty',    a.buy_qty.cumsum()) # hold qty
    a.insert(4, 'sell_price',  a.cur_price*inc_perc)
    a.insert(5, 'acum_amount', (a.cur_price*a.buy_qty).cumsum()) # hold cost
    a.insert(6, 'profit',      a.sell_price*a.acum_qty-a.acum_amount)

    return a

if __name__ == '__main__':
    df = create_buy_table(inc_perc=1.15)
    print(df)
    print()

    df = create_buy_table(interval=0.05, inc_perc=1.15)
    print(df.head(30))
    print()

