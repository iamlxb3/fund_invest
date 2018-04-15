import os
import time
import datetime
import ntpath
import pandas as pd

def fund_csv_reader(csv_dir, chosen_funds=None):
    '''read the csvs and make sure they have the same length'''
    fund_csv_list = os.listdir(csv_dir)
    fund_csv_path_list = [os.path.join(csv_dir, x) for x in fund_csv_list]
    all_funds_id = set([x[:-4] for x in fund_csv_list])
    if chosen_funds is None:
        chosen_funds = all_funds_id.copy()
    dates = set()

    # get a vague range of date
    fund_df_list = []
    fund_id_list = []

    for fund_csv_path in fund_csv_path_list:
        fund_df = pd.read_csv(fund_csv_path)
        fund_id = ntpath.basename(fund_csv_path)[:-4]
        if fund_id not in chosen_funds:
            continue
        for i, row in fund_df.iterrows():
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
            fund_df.at[i, 'date'] = new_date
            #row['date'] = new_date
        fund_df_list.append(fund_df)
        fund_id_list.append(fund_id)

    # get the smallest set of dates
    for fund_df in fund_df_list:
        temp_dates = set(fund_df['date'])
        if not dates:
            dates = temp_dates
        else:
            dates = dates.intersection(temp_dates)

    # make sure all fund df have the same date length
    fund_dfs = {}
    for i, fund_df in enumerate(fund_df_list):
        fund_id = fund_id_list[i]
        fund_df = fund_df[fund_df['date'].isin(dates)]
        fund_dfs[fund_id] = fund_df

    sorted_dates = sorted(list(dates))
    return sorted_dates, fund_dfs