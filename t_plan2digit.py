#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from all import StockInfo

if __name__ == '__main__':
    si = StockInfo()

    in_filename = 'tmp'
    in_fd  = open(in_filename)
    no = 0
    while 1:
        line = in_fd.readline()
        if not line:
            break
        no += 1

        pos = line.find(' ')
        s = line[pos+1:len(line)-1]
        base,free,new,bonus = si.plan2digit(s)

        print(s)
        print(base, free, new, bonus)
        print()
