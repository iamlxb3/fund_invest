import numpy as np
import pandas as pd


initial_salary = 130000 # 起始资金
max_salary = 350000 # 到手工资上限
keep_percent_per_year = 0.6 # 每年存下来的钱（百分比）
add_salary_frequency = 2 # 每两年涨一次薪水
year_add_percent = 0.2 # 每一次的工资涨幅
fund_profit_percent = 0.1 # 投资年化收益率，假设存下来的钱全部用于投资

compute_year = 3
salary = initial_salary
money = 0

for i in range(compute_year):
    if (i+1) % add_salary_frequency == 0:
        salary += year_add_percent * salary # 今年工资
        if salary >= max_salary:
            salary = max_salary
    invest_profit = (fund_profit_percent + 1) * money # 上一年投资盈利
    kept_salary = salary * keep_percent_per_year # 去除开支之后今年存下来的钱
    money = kept_salary + invest_profit # 今年存下的工资 + 上一年的投资获利

print ("计算{}年后\n存款达到{}元\n到手年薪{}\n起始年薪{}\n投资年化收益率{}\n调薪频率每{}年一次\n调薪涨幅{}\n每年存钱百分比{}"
       .format(compute_year,
               money,
               salary,
               initial_salary,
               fund_profit_percent,
               add_salary_frequency,
               year_add_percent,
               keep_percent_per_year))

#
