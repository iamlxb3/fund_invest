import numpy as np
import time
import datetime

class Fund():

    def __init__(self, capital):
        self.capital = capital
        self.is_open = False
        self.is_close = True
        self.open_date = None

    def open_pos(self):
        pass

    def close_pos(self):
        pass








class Rebalance:

    def __init__(self, fund_dfs, sorted_dates, capital=1):
        self.capital = capital
        self.sorted_dates = sorted_dates

        # get the initial money
        self.fund_ids = list(fund_dfs.keys())
        fund_num = len(self.fund_ids)
        self.orgin_average_capital = capital/fund_num

        self.fund_dfs = fund_dfs


    def reset(self):
        self.fund_capital_dict = {id: self.orgin_average_capital for id in self.fund_ids}
        self.capital_hist = []
        self.buy_date_hist = []
        self.sell_date_hist = []



    def _convert_date_str_to_date(self, date_str_list):
        date_obj_list = []
        for date_str in date_str_list:
            date_obejct_temp = time.strptime(date_str, '%Y-%m-%d')
            date_obejct = datetime.datetime(*date_obejct_temp[:3])
            date_obj_list.append(date_obejct)
        return date_obj_list


    def _date_range(self, sorted_dates, date_range):
        if date_range:
            date_range = self._convert_date_str_to_date(date_range)
            sorted_date_objs = self._convert_date_str_to_date(sorted_dates)
            sorted_date_objs = [date_obj for date_obj in sorted_date_objs if date_range[0] <= date_obj <= date_range[1]]
            sorted_dates = [date_obj.strftime("%Y-%m-%d") for date_obj in sorted_date_objs]

        return sorted_dates


    def best_profit(self, trade_frequency=1, date_range=None):
        self.reset()
        sorted_dates = self._date_range(self.sorted_dates, date_range)
        for i, date in enumerate(sorted_dates):
            if i <= len(sorted_dates) - 1 - trade_frequency and i % trade_frequency == 0:

                # get the best profit for this date
                best_close = float('-inf')
                best_fund = None
                buy_date = date
                sell_date = sorted_dates[i + trade_frequency]

                for fund, fund_df in self.fund_dfs.items():
                    buy_close = fund_df.loc[fund_df['date']==buy_date, 'close'].values[0]
                    sell_close = fund_df.loc[fund_df['date']==sell_date, 'close'].values[0]
                    profit_close = (sell_close - buy_close) / buy_close
                    if profit_close > best_close:
                        best_close = profit_close
                        best_fund = fund

                #print ("buy_date: {}, best_close: {}, best_fund: {}".format(buy_date, best_close, best_fund))


                # buy if the best_close is positive
                if best_close > 0:
                    total_capital = sum(self.fund_capital_dict.values())
                    for fund, _ in self.fund_capital_dict.items():
                        if fund == best_fund:
                            self.fund_capital_dict[fund] = total_capital * (1 + best_close)
                        else:
                            self.fund_capital_dict[fund] = 0.0
                    # print(self.fund_capital_dict)
                else:
                    continue


        return self.fund_capital_dict


    def trade(self, trade_frequency=1, is_rebalance=True, date_range=None, is_verbose=True):
        self.reset()
        # TODO, unitest this function
        sorted_dates = self._date_range(self.sorted_dates, date_range)

        if is_verbose:
            print ("sorted_dates: ", sorted_dates)

        for i, date in enumerate(sorted_dates):
            if i <= len(sorted_dates) - 1 - trade_frequency and i % trade_frequency == 0:
                buy_date = date
                sell_date = sorted_dates[i+trade_frequency]
                # open position and calculate profit
                for fund, capital in self.fund_capital_dict.items():
                    fund_df = self.fund_dfs[fund]
                    close_buy = fund_df.loc[fund_df['date']==buy_date, 'close'].values[0]
                    close_sell = fund_df.loc[fund_df['date']==sell_date, 'close'].values[0]
                    profit = ((close_sell - close_buy) / close_buy) * capital
                    self.fund_capital_dict[fund] += profit

                # rebalance
                if is_rebalance:
                    total_capital = np.sum(list(self.fund_capital_dict.values()))
                    average_capital = total_capital / len(self.fund_capital_dict.keys())
                    self.fund_capital_dict = {id: average_capital for id, _ in self.fund_capital_dict.items()}

                # checkpoint
                capital_now = sum(self.fund_capital_dict.values())

                self.capital_hist.append(capital_now)
                self.buy_date_hist.append(date)
                self.sell_date_hist.append(sell_date)

        return self.fund_capital_dict, list(zip(self.capital_hist, self.buy_date_hist, self.sell_date_hist))