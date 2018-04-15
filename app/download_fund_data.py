import sys
import os
import pandas

current_dir = os.path.dirname(os.path.abspath(__file__))
top_dir = os.path.dirname(current_dir)
fund_dir = os.path.join(top_dir, 'data', 'fund')

import tushare as ts

# reference: https://xueqiu.com/3926587841/77555717
# https://zhuanlan.zhihu.com/p/300597614
# https://zhuanlan.zhihu.com/p/24920904

# 国内股票ETF
# 510050 [华夏上证ETF]
# 510330 [华夏沪深_华夏沪深300ETF]
# 510300 [华泰柏瑞沪深300ETF]
# 510500 [中证500ETF]
# 510440 [中证500 EFF]
# 159926 [嘉实中证中期国债ETF]
# 159915 [易方达创业板ETF]
# 159919 [嘉实沪深300ETF]

# 海外股票ETF
# 510900 [易方达恒生H股ETF]
# 159920 [华夏恒生ETF]

# 债券型ETF
# 511220 [海富通上证可质押城投债]
# 511010 [国泰上证国债ETF]

# 大宗商品ETF
# 518880 [华安黄金易ETF] 50.67亿元
# 159934 [易方达黄金ETF] 11.45亿元

# 513500 标普500
# 513100 纳指ETF

# TODO add more fund list

# 国内股票
gngp_etf = ['510050', '510330', '510300', '510500', '510440', '159926', '159915', '159919']

# 海外股票
hwgp_etf = ['510900', '159920']

# 债券型ETF
zq_etf = ['511220', '511010']

# 大宗商品
dzsp_etf = ['518880', '159934']

# 其他
others = ['513500', '513100']

fund_id_list = gngp_etf + hwgp_etf + zq_etf + dzsp_etf + others


# ----------------------------------------------------------------------------------------------------------------------
# skip the downloaded
# ----------------------------------------------------------------------------------------------------------------------
is_skip = True
if is_skip:
    fund_ids = os.listdir(fund_dir)
    fund_ids_set = set([x[:-4] for x in fund_ids])
# ----------------------------------------------------------------------------------------------------------------------


for fund_id in fund_id_list:
    if fund_id in fund_ids_set and is_skip:
        print ("{} has already been downloaded, skip!".format(fund_id))
        continue
    a = ts.get_hist_data(fund_id, ktype='M') #一次性获取全部日k线数据
    save_path = os.path.join(fund_dir, '{}.csv'.format(fund_id))
    try:
        a.to_csv(save_path)
    except AttributeError:
        print ("Cannot download {}! Skip!".format(fund_id))
    else:
        print ("save {} to {}".format(fund_id, save_path))



