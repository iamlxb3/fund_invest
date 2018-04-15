import sys
import os
import pandas as pd

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
# is_plot
is_plot = True

# filter fund
chosen_funds = {'513100', '513500', '510500','510900', '510050', '510300'}

# chosen date range
#date_range = ('2014-01-30', '2017-01-30')
date_range = ('2017-01-30', '2018-03-30')

capital = 100
trade_frequency = 12 # month
# ----------------------------------------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------------------------------------------------
# read and clean dfs
# ----------------------------------------------------------------------------------------------------------------------
sorted_dates, fund_dfs = fund_csv_reader(fund_dir, chosen_funds=chosen_funds)
print("sorted_dates: ", sorted_dates)

delete_ids= []
for id, df in fund_dfs.items():
    if id not in chosen_funds:
        delete_ids.append(id)

for id in delete_ids:
    pop_success = fund_dfs.pop(id, None)
    if pop_success is None:
        raise Exception("Check chosen_fund ids! {} is not valid!".format(id))


#print (sorted_dates)
#print ([df.shape for _, df in fund_dfs.items()])

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
fund_capital_dict, hist = rebalancer.trade(trade_frequency=trade_frequency, is_rebalance=True,
                                           date_range=date_range)
sell_date_hist = [x[2] for x in hist]
capital_hist = [x[0] for x in hist]
max_drawdown = min(capital_hist)
print ("\ncapital_hist: ", hist)
print (fund_capital_dict)
print ("\nrebanlance total: {}, max_drawdown: {}".format(sum(list(fund_capital_dict.values())), max_drawdown))

# (2.) possible highest profit
fund_capital_dict = rebalancer.best_profit(trade_frequency=trade_frequency, date_range=date_range)
print ("--------------------------------------------------------------------------")
print (fund_capital_dict)
print ("possible highest total: {}".format(sum(list(fund_capital_dict.values()))))

# ----------------------------------------------------------------------------------------------------------------------


if is_plot:
    # plot
    # TODO, add chosen_fund name
    import seaborn as sns
    sns.set_style("darkgrid")

    import matplotlib.pyplot as plt
    x = [x for x in range(len(capital_hist))]
    date_xticks = sell_date_hist
    plt.xticks(x, date_xticks)
    plt.plot(x, capital_hist)
    plt.show()


    