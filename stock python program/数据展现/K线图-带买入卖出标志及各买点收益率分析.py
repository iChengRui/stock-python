#usr/bin/env python2
# -*- coding: UTF-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import matplotlib.pyplot as plt
import matplotlib.finance as finan
import pandas as pd
import numpy as np
import pymysql as psql

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def tag(table=None, find=None):
    if (table is None):
        raise
    length = len(find)
    j = 0
    i = 0
    c = []
    while (length > i):
        if (table[j] < find[i]):
            j += 1
        elif (table[j] == find[i]):
            c.append(j)
            # 一天内可能有多个买入或卖出原因
            i += 1
        else:
            print(u"表中日期" + str(table[j]) + u",寻找的日期" + str(find[i]))
            raise
    return c


conn = psql.connect(host='localhost', user='root', password='krvd#l6', port=3306, database='stock', charset='utf8')
cursor = conn.cursor()


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


def shouyiTable(cursor=None, stockname=None):
    if (cursor is None or stockname is None):
        raise ValueError
    QueryStr = "create temporary table Mairu select riqi,yuanyin from MaiRuBiao where stockname='" + \
               stockname + "' order by riqi"
    cursor.execute(QueryStr)
    QueryStr = "select Mairu.riqi,yuanyin,shoupanjia from Mairu left join " + stockname + \
               " on Mairu.riqi=" + stockname + ".riqi order by Mairu.riqi"
    cursor.execute(QueryStr)
    np_buy = np.array(cursor.fetchall())
    QueryStr = "drop table Mairu"
    cursor.execute(QueryStr)
    QueryStr = "create temporary table Maichu select distinct riqi from MaiChuBiao where stockname='" \
               + stockname + "' order by riqi"
    cursor.execute(QueryStr)
    QueryStr = "select Maichu.riqi,shoupanjia from Maichu left join " + stockname + " on Maichu.riqi=" \
               + stockname + ".riqi order by Maichu.riqi"
    cursor.execute(QueryStr)
    np_sell = np.array(cursor.fetchall())
    QueryStr = "drop table Maichu"
    cursor.execute(QueryStr)
    Pdhuoli, jianshao = get_huoli(np_buy, np_sell)

    return Pdhuoli.groupby('yuanyin').describe()


class candlestickploter:
    def __init__(self, cur, stockindex=0):
        # 获取所有股票的代码
        self.cursor = cur
        self.stockcount = self.cursor.execute("select stockname,MingCheng,LeiBie from XuanZe")
        self.stockcount -= 1  # 序号从零开始，最后一个比stockcount小，才能保证+1时取到最后一个
        self.stocklist = np.array(self.cursor.fetchall())
        self.stockindex = stockindex
        # 绘制第一个图
        self.GetInfo()
        self.fig, (self.ax, self.ax2, self.ax3) = plt.subplots(3, 1, sharex=True,
                                                               gridspec_kw={'height_ratios': [11, 5, 3]},
                                                               figsize=(18, 15))
        self.ax.tick_params(length=0)
        self.ax2.tick_params(length=0)

        self.fig.canvas.mpl_connect('key_press_event', self)
        self.PlotIt()
        plt.show()

    def GetInfo(self):
        # 获取所有的历史数据
        self.Kongji = []
        while True:
            self.QueryStr = "select kaipanjia,shoupanjia,zuigaojia,zuidijia,chengjiaoliang,riqi from " + \
                            self.stocklist[self.stockindex][0]
            self.InfoRow = self.cursor.execute(self.QueryStr)
            self.Df = self.cursor.fetchall()
            self.Df = np.array(self.Df)
            if len(self.Df) > 0:
                break
            else:
                self.Kongji.append(self.stocklist[self.stockindex][1])
                if self.stockindex < self.stockcount:
                    self.stocklist = np.delete(self.stocklist, self.stockindex, 0)
                    self.stockcount -= 1
                else:
                    print
                    ",".join(self.Kongji) + ",all is empty set,jump\n"
                    raise

        # 获取买入日期及原因
        self.QueryStr = "select riqi,yuanyin from MaiRuBiao where stockname='" + \
                        self.stocklist[self.stockindex][
                            0] + "' order by riqi"
        self.cursor.execute(self.QueryStr)
        self.Buy = np.array(self.cursor.fetchall())
        if len(self.Buy) > 0:
            self.Buyindex = tag(self.Df[:, 5], self.Buy[:, 0])
            self.Buy = self.Buy[:, 1]
        else:
            self.Buyindex = []
            self.Buy = []
        # 获取卖出日期及原因
        self.QueryStr = "select riqi,yuanyin from MaiChuBiao where stockname='" + self.stocklist[self.stockindex][
            0] + "' order by riqi"
        self.cursor.execute(self.QueryStr)
        self.Sell = np.array(self.cursor.fetchall())
        if len(self.Sell) > 0:
            self.Sellindex = tag(self.Df[:, 5], self.Sell[:, 0])
            self.Sell = self.Sell[:, 1]
        else:
            self.Sellindex = []
            self.Sell = []
        # 时间间隔导致图中对应的图形之间有间隔
        self.riqi = np.arange(1, 1 + self.InfoRow)
        # 关键点
        self.data = zip(self.riqi, self.Df[:, 0], self.Df[:, 1], self.Df[:, 2], self.Df[:, 3])
        self.MA5 = pd.rolling_mean(self.Df[:, 1], 5)
        self.volume = self.Df[:, 4]
        self.volume /= np.float32(min(self.volume))
        # 出现遗失数据，当开盘价等于收盘价的时候
        self.pos = self.Df[:, 0] - self.Df[:, 1] < 0
        self.neg = self.Df[:, 0] - self.Df[:, 1] > 0
        self.neu = self.Df[:, 0] - self.Df[:, 1] == 0
        # 对买入原因对应的收益进行统计
        self.shouyi = shouyiTable(cursor=self.cursor, stockname=self.stocklist[self.stockindex][0])
        self.shouyi.values[:, 1:] = np.round(self.shouyi.values[:, 1:] * 100, 2)  # 将数据换算成以百分比%为单位的数据

    def PlotIt(self):
        # 画图
        self.ax.cla()
        self.ax2.cla()
        self.ax3.cla()

        finan.candlestick_ochl(self.ax, self.data, colorup=u'r', colordown=u'g', alpha=0.5)
        self.ax.set_ylim(min(self.Df[:, 3]) * 0.9, max(self.Df[:, 2]) * 1.1)
        self.ax.plot(self.riqi, self.MA5)
        # 标注买入标志
        for xu, index in enumerate(self.Buyindex):
            if xu > 0:
                if index == oldindex:
                    LocPlace += self.Df[index, 3] * 0.02
                else:
                    oldindex = index
                    LocPlace = self.Df[index, 3]
            else:
                oldindex = index
                LocPlace = self.Df[index, 3]
            self.ax.text(index, LocPlace, str(self.Buy[xu]), color='b', fontsize=10)
        # 标注卖出标志
        for xu, index in enumerate(self.Sellindex):
            if xu > 0:
                if index == oldindex:
                    LocPlace += 0.02 * self.Df[index, 2]
                else:
                    oldindex = index
                    LocPlace = self.Df[index, 2]
            else:
                oldindex = index
                LocPlace = self.Df[index, 2]
            self.ax.text(index, LocPlace, str(self.Sell[xu]), color='k', fontsize=10)
        if len(self.Kongji) > 0:
            self.title = ",".join(self.Kongji) + u" 无历史数据，已跳过\n" + self.stocklist[self.stockindex][1] + " " + \
                         self.stocklist[self.stockindex][2] + " " + str(self.stockindex)
        else:
            self.title = self.stocklist[self.stockindex][1] + " " + self.stocklist[self.stockindex][2] + " " + str(
                self.stockindex)
        self.fig.suptitle(self.title, fontsize=16)
        self.ax2.bar(self.riqi[self.pos], self.volume[self.pos], color='r', width=1, align='center')
        self.ax2.bar(self.riqi[self.neg], self.volume[self.neg], color='g', width=1, align='center')
        self.ax2.bar(self.riqi[self.neu], self.volume[self.neu], color='b', width=1, align='center')

        self.ax2.set_ylim(0, max(self.volume) + 1)
        self.ax2.set_xlim(0, self.InfoRow + 1)
        # 绘制收益统计表
        self.ax3.xaxis.set_ticks([])  # 除去框线
        self.ax3.yaxis.set_ticks([])
        # loc='upper center' bbox=[0, 0, 1, 1]
        self.ax3.table(cellText=self.shouyi.values, rowLabels=self.shouyi.index,
                       rowColours=None, colLabels=self.shouyi.columns.levels[1], bbox=[0, 0, 1, 1])
        self.ax3.set_xlabel(u'除个数(count)外，所有列均以百分比%为单位', size=12)

        self.fig.canvas.draw()

    def __call__(self, event):
        if event.key not in ('a', 'f'):
            return
        if event.key == 'a':
            if self.stockindex > 0:
                self.stockindex -= 1
                self.GetInfo()
                self.PlotIt()
        elif event.key == 'f':
            if self.stockindex < self.stockcount:
                self.stockindex += 1
                self.GetInfo()
                self.PlotIt()


M = candlestickploter(cursor, stockindex=82)
