#!/bin/bash
#自动导入每日股票数据，更新除权除息，确定卖出的股票，将卖出股票的数据导出，确定买入股票，将买入的股票数据导出
#
#
#自动导入每日股票数据
##确定是否有除权除息信息
if [ $# -eq 0 ]
then
  echo "请补充除权除息信息"
  exit 1
fi

if [ $1 != "无除权除息" ] && [ $1 != "有除权除息" ]
then
  echo "请补充除权除息信息"
  exit 1
fi

##确定有昨日的数据
filename="/home/acer/桌面/股票/InsertValue.csv"
if [ -e  $filename ]
then
rm -f $filename
fi
filename="/home/acer/桌面/股票/Table.xls"
filetime=`stat -c %Y "$filename"`
nowtime=`date +%s`
##确定是否有今日的数据
if [ $[ $nowtime - $filetime ] -gt 86400 ]
then
echo "每日股票数据没有更新，请更新后再运行"
exit 1
fi
#################################################
##变更它的名字
#mv $filename ${filename/%Table.xls/InsertValue.csv}
#################################################
##利用程序将将数据格式化并变更其文件名
gawk -f au "$filename" >"${filename/%Table.xls/InsertValue.csv}"
filename="${filename/%Table.xls/InsertValue.csv}"
##利用程序将数据插入
echo "录入数据"
mysql -uroot -p < "$filename"
#
#
#更新除权除息
if [ $1 = "有除权除息" ]
then
filename="/home/acer/桌面/迅雷下载/"`date +%F`.csv
if [ -e  $filename ]
then
##变更它的名字
filename2=${filename%/*}"/chuquanchuxi.csv"
mv $filename $filename2
##利用程序将数据插入
echo "更新除权除息"
chuquanchuxi -auto
else
echo "每日除权除息数据没有更新，请补充除权除息资料"
exit 2
fi
fi
#
#
#确定卖出的股票
echo "卖出"
sell4 -auto
#导出卖出的股票
 mysql_query_output 是 "/home/acer/桌面/股票/maichu.txt" "select distinct mid(stockname,3,6) from MaiChuBiao where riqi=curdate()"

##确定是否有昨日的数据
##filename="/home/acer/桌面/股票/maichu.txt"
##if [ -e  "$filename" ]
##then
##rm -f $filename
##fi
##mysql -uroot -p <<EOF
##use stock;
##select distinct mid(stockname,3,6) from MaiChuBiao where riqi=curdate() into outfile '/home/acer/桌面/股票/maichu.txt';
##EOF


#确定买入的股票
echo "买入"
Qushi-Buy2 -auto
#导出买入的股票
 mysql_query_output 是 "/home/acer/桌面/股票/mairu.txt" "select distinct mid(stockname,3,6) from MaiRuBiao where riqi=curdate()"
