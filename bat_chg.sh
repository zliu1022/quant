#!/bin/bash

#ts_code='002475.SZ'
ts_code='000425.SZ'
#ts_code='002456.SZ'

num=0

echo $ts_code

for chg in 0.1 0.15 0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7
#for chg in 0.55 0.6 0.65 0.7
#for chg in 0.7
do
    for interval in 0.01 0.02 0.025 0.03 0.035 0.04 0.045 0.05
    do
        log_name=$ts_code\_$chg\_$interval'.txt'
        echo $log_name
        ./StockDraw.py $ts_code $chg $interval > $log_name
        num=`expr $num + 1`
    done
    echo
done

echo total $num

