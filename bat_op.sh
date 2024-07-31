#!/bin/bash

start_date="20220315"

codelist='002456'
for code in $codelist
do
    ./StockOp.py $code $start_date 1.2  > $code.$start_date.20%.sim
    ./StockOp.py $code $start_date 1.25 > $code.$start_date.25%.sim
    ./StockOp.py $code $start_date 1.3  > $code.$start_date.30%.sim
    ./StockOp.py $code $start_date 1.35 > $code.$start_date.35%.sim
    ./StockOp.py $code $start_date 1.4  > $code.$start_date.40%.sim
    ./StockOp.py $code $start_date 1.45 > $code.$start_date.45%.sim
    ./StockOp.py $code $start_date 1.5  > $code.$start_date.50%.sim
    ./StockOp.py $code $start_date 1.55 > $code.$start_date.55%.sim
done

codelist='002475 600519 002273 000425 002456'
for code in $codelist
do
    grep norm $code.$start_date*
    echo
done

