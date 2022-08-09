# -*- coding:utf-8 -*-
import os
import tushare as ts

ROOT_PATH=os.path.abspath(os.path.dirname(os.getcwd()))
ROOT_TXT_PATH=ROOT_PATH+"/stock_py/SData/"
class StockSingle:
    _instance = None
    _flag = True
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance   # 返回的是内存地址

    def __init__(self):
        if StockSingle._flag:  # 如果init 没有执行
            self._uindex=0
            self.haoshi=0
            self._trade_date_now=''
            self.trade_stock_now_file_path=''
            self.f = None
            ts.set_token('0603f0a6ce3d7786d607e65721594ed0d1c23b41d6bc82426d7e4674')
            self.pro = ts.pro_api()
            StockSingle._flag = False  # 表示执行过init

    @property
    def uindex(self):
        return self._uindex
    
    @uindex.setter
    def uindex(self,a):
        self._uindex = a

    @property
    def trade_date_now(self):
        return self._trade_date_now

    @trade_date_now.setter
    def trade_date_now(self,date):
        self._trade_date_now = date
        self.trade_stock_now_file_path = ROOT_TXT_PATH+date+"-rps.txt"
        self.f = open(self.trade_stock_now_file_path, "w+") 
