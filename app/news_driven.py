import sys
import os
import numpy as np
import pandas as pd
import time
import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
top_dir = os.path.dirname(current_dir)
a_share_stocks_dir = os.path.join(top_dir, 'data', 'all_a_share_stocks')

def process_stock(stock_id):
    stock_path = os.path.join(a_share_stocks_dir, "{}.csv".format(stock_id))
    df = pd.read_csv(stock_path)

    # date, open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20, v_ma5, v_ma10, v_ma20, turnover
    df = df[['date', 'close', 'volume']]

    # align dates
    for i, row in df.iterrows():
        date_str = row['date']
        month = str(date_str[-5:-3])
        day = int(date_str[-2:])
        if 23 <= day <= 31:
            if month == '02':
                day = 28
            else:
                day = 30
                # TODO, add 1 < day < 7
        new_date = date_str[:-2] + str(day)
        df.at[i, 'date'] = new_date

    # close data
    data = dict(zip(df.date.values, df.close.values))

    return data

def date_align(data1, data2):
    data1_values = []
    data2_values = []
    dates = []
    for date, data1_value in data1.items():
        if date in data2:
            data2_value = data2[date]
            data1_values.append(data1_value)
            data2_values.append(data2_value)
            dates.append(date)

    assert len(data1_values) == len(data2_values), "data1, data2 has different length!"
    return tuple(data1_values), tuple(data2_values), sorted(dates)

def _convert_date_str_to_date(date_str_list):
    date_obj_list = []
    for date_str in date_str_list:
        date_obejct_temp = time.strptime(date_str, '%Y-%m-%d')
        date_obejct = datetime.datetime(*date_obejct_temp[:3])
        date_obj_list.append(date_obejct)
    return date_obj_list


def _date_range(sorted_dates, date_range):
    if date_range:
        date_range = _convert_date_str_to_date(date_range)
        sorted_date_objs = _convert_date_str_to_date(sorted_dates)
        sorted_date_objs = [date_obj for date_obj in sorted_date_objs if date_range[0] <= date_obj <= date_range[1]]
        sorted_dates = [date_obj.strftime("%Y-%m-%d") for date_obj in sorted_date_objs]

    return sorted_dates

# ----------------------------------------------------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------------------------------------------------
target_id = '000063' # 中兴
min_month = 10 # min month to compare
blocks = [] # only compare stocks in these blocks
# TODO, add more ids from US stock market, etc.
compare_ids = set(x[:-4] for x in os.listdir(a_share_stocks_dir))
include_ids = []
date_range = ("2013-01-30",  '2017-01-30')
# exclude itself
compare_ids -= {target_id}
verbose = False
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# find the most correlated stocks
# ----------------------------------------------------------------------------------------------------------------------
# read target stock
target_stock_data_copy = process_stock(target_id)
# set date range for comparision
sorted_dates = set(_date_range(sorted(target_stock_data_copy.keys()), date_range))

target_stock_data = {}
# pop key
for key, value in target_stock_data_copy.items():
    if key in sorted_dates:
        target_stock_data[key] = value
print ("sorted_dates: ", sorted_dates)

corrcoef_list = []
for compare_id in compare_ids:

    # process single stock, make sure the end date for each month is same
    compare_id_data = process_stock(compare_id)

    # date align for different stocks
    target_stock_values, compare_id_values, dates = date_align(target_stock_data, compare_id_data)

    # filter min month
    if len(target_stock_values) < min_month:
        print ("{} too short! Only {} month overlap!".format(compare_id, len(compare_id_values)))
        continue
    else:
        if verbose:
            print("compare on dates: ", dates)

    # compute the correlation between 2 stocks
    corrcoef = np.corrcoef([target_stock_values, compare_id_values])[1,0]

    #
    corrcoef_list.append((compare_id, corrcoef, len(target_stock_values)))

# sort
top10_corrcoef_list = sorted(corrcoef_list, key=lambda x:x[1], reverse=True)[:10]
last10_corrcoef_list = sorted(corrcoef_list, key=lambda x:x[1])[0:10]





for id, corrcoef, length in top10_corrcoef_list:
    print ("{}:{}-compare_month:{}".format(id, corrcoef, length))
print ("-----------------------------------")
for id, corrcoef, length in last10_corrcoef_list:
    print ("{}:{}-compare_month:{}".format(id, corrcoef, length))
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# TODO predict future movement
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
