#!/bin/bash

file="stat-55.0%-0.03-mktvalue-1000-inf.csv"
line_count=$(wc -l < "$file")

for line_number in $(seq 1 $line_count)
do
    if [ $line_number -lt 22 ] ; then
        continue
    elif [ $line_number -gt 100 ] ; then
        break
    fi

    ret=$(sed -n "${line_number}p" "$file")
    code=${ret%%,*}
    if [ $code = "ts_code" ] ; then
        continue
    fi
    f_name=${code}_sim_chg_monthly_20200701_20230615_0.55_0.03.sim

    echo $line_number $code $f_name
    ./t_StockSim.py $code 0.55 0.03 > $f_name
done

