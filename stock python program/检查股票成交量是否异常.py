#检查成交量是否异常
import numpy as np
import pymysql as psql
conn=psql.connect(host='localhost',user='root',password='krvd#l6',port=3306,database='stock',charset='utf8')
cursor=conn.cursor()
stockcount=cursor.execute("select stockname from XuanZe")
stocklist=cursor.fetchall()
stockcount=len(stocklist)
stockindex=0
abnormalVolume=[]
abnormalDate=[]
blankStock=[]
while(stockindex<stockcount):
    QueryStr="select max(chengjiaoliang),min(chengjiaoliang) from " + stocklist[stockindex][0]
    InfoRow=cursor.execute(QueryStr)
    Df=cursor.fetchall()
    Df=np.array(Df)
    #部分股票可能没有数据
    if Df[0,1] is not None:
        #最高成交量超过最低成交量50倍以上
        if Df[0,0]/Df[0,1]> 50 :
            abnormalVolume.append(stocklist[stockindex][0])
            QueryStr="select riqi from "  + stocklist[stockindex][0] + " where chengjiaoliang="+ str(Df[0,1])
            InfoRow=cursor.execute(QueryStr)
            T=cursor.fetchall()
            abnormalDate.append(str(T[0][0]))
    else:
        blankStock.append(stocklist[stockindex][0])
    stockindex+=1
for name,riqi in zip(abnormalVolume,abnormalDate):
    print(name+ " : "+riqi)
print(u"空数据表")
print(blankStock)
