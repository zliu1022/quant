#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

# method1:
class Info():
    def req_basic(self, para):
        return "class basic"
    def req_bonus(self, para):
        return "class bonus"
    def req_day(self, para):
        return "class day"
    def Default(self, para):
        return "class Invalid"
    def map_req(self, name):
        req_name = "req_" + str(name)
        fun = getattr(self, req_name, self.Default)
        return fun

# method2:
def req_basic(para):
    return "basic"
def req_bonus(para):
    return "bonus"
def req_day(para):
    return "day"
def Default(para):
    return "Invalid"
reqdict = {
    'basic': req_basic,
    'bonus': req_bonus,
    'day': req_day
}

def map_req(name):
    fun = reqdict.get(name, Default)
    return fun

if __name__ == '__main__':
# ref: https://cloud.tencent.com/developer/article/1540890

    if len(sys.argv) != 3:
        print('t_case.py [basic|bonus|day] para')
        quit()

    info = Info()
    func = info.map_req(sys.argv[1])
    print(func(sys.argv[2]))

    func = map_req(sys.argv[1])
    print(func(sys.argv[2]))

