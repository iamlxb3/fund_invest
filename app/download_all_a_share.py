import sys
import os
import pandas
import pickle

current_dir = os.path.dirname(os.path.abspath(__file__))
top_dir = os.path.dirname(current_dir)
a_share_stocks_dir = os.path.join(top_dir, 'data', 'all_a_share_stocks')
stock_id_set = os.path.join(top_dir, 'data', 'stock_id.set')

import tushare as ts
stock_id_set = pickle.load(open(stock_id_set, 'rb'))
downloaded = os.listdir(a_share_stocks_dir)
downloaded = set([x[:-4] for x in downloaded])

# ----------------------------------------------------------------------------------------------------------------------

print ("downloaded: ", downloaded)
print ("stock_id_set: ", stock_id_set)

for stock_id in stock_id_set:
    if stock_id in downloaded:
        print ("skip: ", stock_id)
        continue
    try:
        data = ts.get_hist_data(stock_id, ktype='M') #一次性获取全部月k线数据
    except OSError:
        print ("Time out! {}".format(stock_id))
    else:
        save_path = os.path.join(a_share_stocks_dir, '{}.csv'.format(stock_id))
        try:
            data.to_csv(save_path)
        except AttributeError:
            print ("Cannot download {}! Skip!".format(stock_id))
        else:
            print ("save {} to {}".format(stock_id, save_path))



