# 导入必要的库
import pandas as pd
import numpy as np
import pymysql as psql

conn = psql.connect(host='localhost', user='root', password='krvd#l6',
                    port=3306, database='stock', charset='utf8')
cursor = conn.cursor()
Queshi = []
stockDict = dict()


# 计算收益率
def get_huoli(np_buy, np_sell):
    buy_len = len(np_buy)
    sell_len = len(np_sell)
    shouyi = []
    yuanyin = []
    i, j = 0, 0
    while (i < buy_len and j < sell_len):
        if (np_sell[j, 0] > np_buy[i, 0]):
            yuanyin.append(np_buy[i, 1])
            shouyi.append(np_sell[j, 1] / np_buy[i, 2] - 1.02)
            i += 1
        else:
            j += 1
    return (pd.DataFrame({'yuanyin': yuanyin, 'shouyi': shouyi}), buy_len - i)


# 获取所有股票列表
# 测试可添加：limit 3
stockcount = cursor.execute("select stockname from XuanZe")
stocklist = cursor.fetchall()
# 查询股票的买卖价格
i = 0
while (i < stockcount):
    QueryStr = """create temporary table Mairu select riqi,yuanyin from
          MaiRuBiao where stockname='""" + stocklist[i][0] + "' order by riqi"
    cursor.execute(QueryStr)
    QueryStr = "select Mairu.riqi,yuanyin,shoupanjia from Mairu left join " \
               + stocklist[i][0] + " on Mairu.riqi=" + stocklist[i][0] \
               + ".riqi order by Mairu.riqi"
    cursor.execute(QueryStr)
    np_buy = np.array(cursor.fetchall())
    QueryStr = "drop table Mairu"
    cursor.execute(QueryStr)
    QueryStr = """create temporary table Maichu select distinct riqi from
        MaiChuBiao where stockname='""" + stocklist[i][0] + "' order by riqi"
    cursor.execute(QueryStr)
    QueryStr = "select Maichu.riqi,shoupanjia from Maichu left join " + \
               stocklist[i][0] + " on Maichu.riqi=" + stocklist[i][0] \
                 + ".riqi order by Maichu.riqi"
    cursor.execute(QueryStr)
    np_sell = np.array(cursor.fetchall())
    QueryStr = "drop table Maichu"
    cursor.execute(QueryStr)
    Pdhuoli, jianshao = get_huoli(np_buy, np_sell)
    Queshi.append(jianshao)
    stockDict[stocklist[i][0]] = Pdhuoli
    i += 1
# 汇总所有的买入原因及收益
AllYuanyinShouyi = pd.DataFrame()
for key in stockDict:
    AllYuanyinShouyi = AllYuanyinShouyi.append(stockDict[key],
                                               ignore_index=True)
# 计算平均收益率并显示
m = AllYuanyinShouyi.groupby('yuanyin').describe().unstack()
print(m)


# 测试使用
for key in stockDict:
    print(key)
    print(stockDict[key])
