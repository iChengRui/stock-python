#删除股票及相关数据
import pymysql as psql
with open("/home/acer/桌面/股票/待处理事项/delete.csv") as f:
    stock=f.read()
stock=stock.splitlines()
conn=psql.connect(host='localhost',user='root',password='krvd#l6',port=3306,database='stock',charset='utf8')
cursor=conn.cursor()
for s in stock:
    cmd="delete from XuanZe where stockname='"+s+"'"
    cursor.execute(cmd)
    cmd="delete from MaiRuBiao where stockname='"+s+"'"
    cursor.execute(cmd)
    cmd="delete from MaiChuBiao where stockname='"+s+"'"
    cursor.execute(cmd)
    cmd="delete from QuShiBiao where stockname='"+s+"'"
    cursor.execute(cmd)
    cmd="drop table "+s
    cursor.execute(cmd)
#添加股票，仅结构，数据待增加
with open("/home/acer/桌面/股票/待处理事项/zengjianeirong.csv") as m:
    line=m.readline()
    while(line):
        stockname,MingCheng,LeiBie=line.split(',')
        LeiBie=LeiBie.strip()
        cmd="create table "+stockname+ " (riqi date NOT NULL,kaipanjia float(7,2) unsigned NOT NULL,"+\
        "shoupanjia float(7,2) unsigned NOT NULL,zuigaojia float(7,2) unsigned NOT NULL,"+\
        "zuidijia float(7,2) unsigned NOT NULL,chengjiaoliang bigint unsigned NOT NULL,houfuquanjia float(8,2) unsigned NOT NULL)"
        cursor.execute(cmd)
        cmd="INSERT INTO XuanZe"+" VALUES('"+stockname+"', '"+MingCheng+"','"+LeiBie+"')"
        cursor.execute(cmd)
        line=m.readline()
