#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

def stat_chg():
    # Step 1: Connect to the MongoDB database and collections
    client = MongoClient('mongodb://localhost:27017/')
    db = client['stk1']
    day_collection = db['day']
    chg_collection = db['chg']

    # Clear the chg collection if it exists
    chg_collection.delete_many({})

    # Step 2: Prompt the user for a start date
    start_date = input("请输入起始日期（格式YYYYMMDD）：")

    # Step 3: Iterate through each document in the day collection
    for doc in day_collection.find():
        symbol = doc.get('symbol')
        if not symbol:
            continue  # Skip if no symbol

        day_data = doc.get('day', [])
        if not day_data or len(day_data) < 3:
            continue  # Need at least 3 days to find minima and maxima

        # Filter day data to include only dates on or after start_date
        day_data_filtered = [d for d in day_data if d['date'] >= start_date]

        if len(day_data_filtered) < 3:
            continue  # Not enough data after filtering

        # Sort the day data in chronological order
        day_data_filtered.sort(key=lambda x: x['date'])

        # Step 4: Process the day data to find local minima and maxima pairs
        min_max_pairs = []
        i = 1  # Start from the second element to access previous and next elements
        state = 'find_min'
        while i < len(day_data_filtered) - 1:
            prev_day = day_data_filtered[i - 1]
            curr_day = day_data_filtered[i]
            next_day = day_data_filtered[i + 1]

            if state == 'find_min':
                # Check for local minimum
                if (curr_day['low'] < prev_day['low']) and (curr_day['low'] < next_day['low']):
                    min_date = curr_day['date']
                    min_value = curr_day['low']
                    state = 'find_max'
                    i += 1  # Move to the next day
                else:
                    i += 1
            elif state == 'find_max':
                # Check for local maximum
                if (curr_day['high'] > prev_day['high']) and (curr_day['high'] > next_day['high']):
                    max_date = curr_day['date']
                    max_value = curr_day['high']
                    # Append the min-max pair
                    min_max_pairs.append({
                        'min_date': min_date,
                        'min': min_value,
                        'max_date': max_date,
                        'max': max_value
                    })
                    state = 'find_min'
                    i += 1  # Move to the next day
                else:
                    i += 1

        # Step 5: Insert the results into the chg collection
        if min_max_pairs:
            chg_doc = {
                'symbol': symbol,
                'min_max': min_max_pairs
            }
            chg_collection.insert_one(chg_doc)
            print(f"Processed symbol: {symbol}, found {len(min_max_pairs)} min-max pairs.")

if __name__ == "__main__":
    stat_chg()
