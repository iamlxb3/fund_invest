import sys
import os
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



# ----------------------------------------------------------------------------------------------------------------------
# config
# ----------------------------------------------------------------------------------------------------------------------
is_verbose = False
is_plot_save_individual_fund = False
comb_num = (3,) # itertools.combinations is robust, you don't have to consider the number of funds
trade_frequency_list = (6,)
#trade_frequency_list = (1,2,3,4,5,6,7,8,9,10,11,12,13,14)
#trade_frequency_list = (1,2) # month
# exclude funds
all_funds = os.listdir(fund_dir)
all_funds = set([x[:-4] for x in all_funds])
exclude_funds = { '510440', '510330', '159934', '159919'} # set()
keep_funds = all_funds - exclude_funds

# chosen date range
date_range = ('2014-01-30', '2017-03-30')
shift_num = 12
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# read in data frames
# ----------------------------------------------------------------------------------------------------------------------
# read the csvs and make sure they have the same length
sorted_dates, orgin_fund_dfs = fund_csv_reader(fund_dir, chosen_funds=keep_funds)
print ("sorted_dates total: {}, from {} to {}".format(len(sorted_dates), sorted_dates[0], sorted_dates[-1]))
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# filter fund
fund_ids = glob(os.path.join(fund_dir, '*.csv'))
fund_ids = [re.findall(r'([0-9]+).csv', x)[0] for x in fund_ids]
fund_ids = set(fund_ids)


# exclude_funds = set()
fund_ids = fund_ids - exclude_funds

all_fund_combs = []
for n in comb_num:
    temp_list = list(itertools.combinations(fund_ids, n))
    for fund_comb in temp_list:
        all_fund_combs.append(fund_comb)
fund_comb_id_name_dict = {i: ','.join(sorted(list(fund_comb))) for i, fund_comb in enumerate(all_fund_combs)}
fund_comb_name_id_dict = {v: k for k, v in fund_comb_id_name_dict.items()}
print ("comb_num: {}".format(len(all_fund_combs)))

all_fund_trade_f_combs = []
for n in comb_num:
    temp_list = list(itertools.combinations(fund_ids, n))
    for fund_comb in temp_list:
        for trade_frequency in trade_frequency_list:
            all_fund_trade_f_combs.append((fund_comb, trade_frequency))


print ("comb_trade_frequency_num: {}".format(len(all_fund_trade_f_combs)))



date_shift_list = []
# shift the date_range by 4 months forward and compute the avg

def _add_1_month_forward(date_str, shift):
    date_obejct_temp = time.strptime(date_str, '%Y-%m-%d')
    date_obejct = datetime.datetime(*date_obejct_temp[:3])
    one_month = relativedelta(months=shift)
    date_obejct += one_month
    new_date_str = date_obejct.strftime("%Y-%m-%d")
    return new_date_str


for j in range(shift_num):
    shift = j + 1
    date_start_str = date_range[0]
    date_end_str = date_range[1]
    date_shift_list.append((_add_1_month_forward(date_start_str, shift), _add_1_month_forward(date_end_str, shift)))


capital = 100
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# read and clean dfs
# ----------------------------------------------------------------------------------------------------------------------
comb_result_list = []

for i, (chosen_fund, trade_frequency) in enumerate(all_fund_trade_f_combs):

    chosen_fund = set(chosen_fund)
    comb_num = len(chosen_fund)

    fund_dfs = copy.copy(orgin_fund_dfs)
    delete_ids= []
    for id, df in fund_dfs.items():
        if id not in chosen_fund:
            delete_ids.append(id)

    for id in delete_ids:
        pop_success = fund_dfs.pop(id, None)
        if pop_success is None:
            raise Exception("Check chosen_fund ids! {} is not valid!".format(id))


    #print (sorted_dates)
    #print ([df.shape for _, df in fund_dfs.items()])
    if is_verbose:
        print ('--------------------------------------------------------------------------')
        print ("Initial capital: {}".format(capital))
        print ("Trade every {} month".format(trade_frequency))
        print ("Chosen fund: {}".format(fund_dfs.keys()))
        print ('--------------------------------------------------------------------------')
    # ----------------------------------------------------------------------------------------------------------------------


    # ----------------------------------------------------------------------------------------------------------------------
    # rebanlance
    # ----------------------------------------------------------------------------------------------------------------------
    rebalancer = Rebalance(fund_dfs, sorted_dates, capital=capital)


    # (1.) rebanlance
    # trade_frequency : trade every N months

    max_drawdown_list = []
    final_capital_list = []
    for date_range in date_shift_list:
        rebalancer.reset()
        fund_capital_dict, hist = rebalancer.trade(trade_frequency=trade_frequency, is_rebalance=True,
                                                   date_range=date_range, is_verbose=is_verbose)
        max_drawdown = min([x[0] for x in hist])
        final_capital = sum(list(fund_capital_dict.values()))
        max_drawdown_list.append(max_drawdown)
        final_capital_list.append(final_capital)

    max_drawdown = np.average(max_drawdown_list)
    final_capital = np.average(final_capital_list)

    if is_verbose:
        # print ("\ncapital_hist: ", hist)
        # print (fund_capital_dict)
        print ("\nrebanlance total: {}, max_drawdown: {}".format(final_capital, max_drawdown))


    # ------------------------------------------------------------------------------------------------------------------
    temp_dict = {}
    temp_dict['final_capital'] = final_capital
    temp_dict['max_drawdown'] = max_drawdown
    temp_dict['trade_frequency'] = trade_frequency
    temp_dict['comb_num'] = comb_num
    comb_str = ','.join(sorted(list(chosen_fund)))
    comb_id = fund_comb_name_id_dict[comb_str]
    temp_dict['comb'] = int(comb_id)

    for id in fund_ids:
        temp_dict[id] = False
    for id in chosen_fund:
        temp_dict[id] = True

    comb_result_list.append(temp_dict)
    if (i + 1) % 100 == 0:
        print ("{}/{} done".format(i+1, len(all_fund_trade_f_combs)))

comb_result_list = sorted(comb_result_list, key=lambda x:x['final_capital'], reverse=True)
top5_comb = comb_result_list[0:5]
worst5_comb = comb_result_list[-5:]

def _print_comb(comb):
    for dict1 in comb:
        fund_true_list = []
        for key, value in dict1.items():
            if key in fund_ids and value:
                fund_true_list.append(key)

        fund_comb = fund_true_list
        capital = dict1['final_capital']
        max_drawdown = dict1['max_drawdown']
        trade_frequency = dict1['trade_frequency']
        print("fund_comb: {}, capital: {}, max_drawdown: {}, frequency: {}"
              .format(fund_comb, capital, max_drawdown, trade_frequency))

print ("-------------------Top5 comb-------------------")
_print_comb(top5_comb)

print ("-------------------Worst5 comb-------------------")
_print_comb(worst5_comb)


# -----------plot---------------
data_visualize = DataVisualizer()
comb_result_df = pd.DataFrame(comb_result_list)
comb_result_df = comb_result_df.sort_values('comb')
print ("df_shape: ", comb_result_df.shape)

plot_save_dir = os.path.join(top_dir, 'plot')
data_visualize.box_plot(comb_result_df, x='comb', y='final_capital', save_path=os.path.join(plot_save_dir,
                                                                                                'comb_1'))

# data_visualize.box_plot(comb_result_df, x='comb', y='max_drawdown', save_path=os.path.join(plot_save_dir,
#                                                                                                 'comb_2'))

data_visualize.box_plot(comb_result_df, x='comb_num', y='final_capital', save_path=os.path.join(plot_save_dir,
                                                                                                'comb_num_1'))
data_visualize.box_plot(comb_result_df, x='comb_num', y='max_drawdown', save_path=os.path.join(plot_save_dir,
                                                                                                'comb_num_2'))

data_visualize.box_plot(comb_result_df, x='trade_frequency', y='final_capital', save_path=os.path.join(plot_save_dir,
                                                                                                'trade_f_1'))
data_visualize.box_plot(comb_result_df, x='trade_frequency', y='max_drawdown', save_path=os.path.join(plot_save_dir,
                                                                                                'trade_f_2'))

if is_plot_save_individual_fund:

    for fund_id in fund_ids:
        data_visualize.box_plot(comb_result_df, x=fund_id, y='final_capital',
                                save_path=os.path.join(plot_save_dir, 'trade_f_{}_1'.format(fund_id)))
        data_visualize.box_plot(comb_result_df, x=fund_id, y='max_drawdown'
                                , save_path=os.path.join(plot_save_dir, 'trade_f_{}_2'.format(fund_id)))

# print ("---------------------fund_comb_id_name_dict---------------------")
# for id, name in sorted(fund_comb_id_name_dict.items(), key=lambda x:x[0]):
#     print ("{}-{}".format(id, name))