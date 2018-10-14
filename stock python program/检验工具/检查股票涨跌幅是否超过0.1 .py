# 检查涨跌幅是否异常
import numpy as np
import pymysql as psql

conn = psql.connect(host='localhost', user='root', password='krvd#l6',
                    port=3306, database='stock', charset='utf8')
cursor = conn.cursor()
stockcount = cursor.execute("select stockname from XuanZe")
stocklist = cursor.fetchall()
stockindex = 0
while (stockindex < stockcount):
    QueryStr = "select riqi,shoupanjia from " + stocklist[stockindex][0]
    InfoRow = cursor.execute(QueryStr)
    Df = cursor.fetchall()
    Df = np.array(Df)
    index = InfoRow - 1
    i = 0
    while (i < index):
        # 注意涨跌幅超过10%的情况，一般在10.5%左右而非准确值
        if (Df[i][1] * 0.895 > Df[i + 1][1] or Df[i][1] * 1.105 < Df[i + 1][1]):
            print(stocklist[stockindex][0] + ' ' + str(Df[i]))
        i += 1
    stockindex += 1
