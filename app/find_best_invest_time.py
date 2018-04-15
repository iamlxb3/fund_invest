import sys
import os
import collections
import pandas as pd
import re
from glob import glob
import itertools
import copy
import numpy as np
import time
import datetime
from dateutil.relativedelta import relativedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
top_dir = os.path.dirname(current_dir)
fund_dir = os.path.join(top_dir, 'data', 'fund')
sys.path.append(top_dir)

from general.csv_reader import fund_csv_reader
from strategy.rebalance import Rebalance
from general.data_visual import DataVisualizer


# trade frequency
trade_frequency = 12

all_funds = os.listdir(fund_dir)
all_funds = set([x[:-4] for x in all_funds])

# exclude funds
#exclude_funds = { '510440', '510330', '159934', '159919'} # set()
#keep_funds = all_funds - exclude_funds
#

sorted_dates, orgin_fund_dfs = fund_csv_reader(fund_dir, chosen_funds=all_funds)
print ("sorted_dates total: {}, from {} to {}".format(len(sorted_dates), sorted_dates[0], sorted_dates[-1]))

invest_open_dict = collections.defaultdict(lambda :[])
invest_close_dict = collections.defaultdict(lambda :[])



for fund, fund_df in orgin_fund_dfs.items():
    fund_df = fund_df[['date', 'close', 'open']]
    #fund_dict = dict(zip(fund_df.date, (fund_df.open, fund_df.close)))
    for i, date in enumerate(sorted_dates):
        if i > len(sorted_dates) - 1 - trade_frequency:
            continue

        open_date = sorted_dates[i]
        close_date = sorted_dates[i + trade_frequency]
        if close_date > sorted_dates[-1]:
            continue

        # compute profit
        close_price = fund_df.loc[fund_df['date']==close_date, 'close'].values[0]
        open_price = fund_df.loc[fund_df['date']==open_date, 'close'].values[0]
        profit = (close_price - open_price) / open_price

        # add to dict
        open_date = str(open_date[5:7])
        close_date = str(close_date[5:7])
        invest_open_dict[open_date].append(profit)
        invest_close_dict[close_date].append(profit)

# compute the average profit for each month
invest_open_list = [(month, np.average(value)) for month, value in invest_open_dict.items()]
invest_open_list = sorted(invest_open_list, key=lambda x:x[1], reverse=True)
invest_close_list = [(month, np.average(value)) for month, value in invest_close_dict.items()]
invest_close_list = sorted(invest_close_list, key=lambda x:x[1], reverse=True)
print ("invest_open_list: ", invest_open_list)
print ("invest_close_list: ", invest_close_list)


# convert to open data-frame
invest_open_df = []
for month, values in invest_open_dict.items():
    for value in values:
        temp_dict = {}
        temp_dict['month'] = month
        temp_dict['profit'] = value
        invest_open_df.append(temp_dict)
invest_open_df = pd.DataFrame(invest_open_df)

# convert to close data-frame
invest_close_df = []
for month, values in invest_close_dict.items():
    for value in values:
        temp_dict = {}
        temp_dict['month'] = month
        temp_dict['profit'] = value
        invest_close_df.append(temp_dict)
invest_close_df = pd.DataFrame(invest_close_df)


# box-plot
data_visualize = DataVisualizer()
data_visualize.box_plot(invest_open_df, x='month', y='profit', title='open_date')
data_visualize.box_plot(invest_close_df, x='month', y='profit', title='close_date')





















