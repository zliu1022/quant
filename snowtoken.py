#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

# 这个方式已经拿不到任何cookie
def get_snowtoken():
    start_t = time.time()
    r = requests.get("https://xueqiu.com", headers={"user-agent":"Mozilla"})
    end_t = time.time()
    t = r.cookies["xq_a_token"]
    u = r.cookies["u"]
    print('update token {} cost {:5.2f}s'.format('', (end_t - start_t)))
    return t

from playwright.sync_api import sync_playwright

def get_snowtoken_pw():
    t = ''
    u = ''
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 无头模式
        context = browser.new_context()
        context.add_init_script("navigator.webdriver = undefined")  # 伪装非自动化访问
        page = context.new_page()
        page.goto("https://xueqiu.com", timeout=60000)  # 超时60秒
        page.wait_for_load_state("networkidle")  # 等待所有请求结束

        cookies = context.cookies()
        for cookie in cookies:
            #print(cookie["name"], cookie["value"])
            if cookie["name"] == 'xq_a_token':
                t = cookie["value"]
                continue
            if cookie["name"] == 'u':
                u = cookie["value"]
                continue
            if t != '' and u != '':
                break

        browser.close()
        return t,u
    
if __name__ == '__main__':
    t,u = get_snowtoken_pw()
    print('xq_a_token:', t)
    print('u:', u)
