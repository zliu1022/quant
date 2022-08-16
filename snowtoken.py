#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def get_snowtoken():
    start_t = time.time()
    r = requests.get("https://xueqiu.com", headers={"user-agent":"Mozilla"})
    end_t = time.time()
    t = r.cookies["xq_a_token"]
    print('update token {} cost {:5.2f}s'.format(t, (end_t - start_t)))
    return t

    
if __name__ == '__main__':
    print('xq_a_token:', get_snowtoken())

