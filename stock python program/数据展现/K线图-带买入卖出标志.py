import sys
reload(sys)
sys.setdefaultencoding('utf8')


import matplotlib.pyplot as plt
import matplotlib.finance as finan
import pandas as pd
import numpy as np
import pymysql as psql
#设置字体，保证可以显示中文
plt.rcParams['font.sans-serif']=['Microsoft YaHei']
plt.rcParams['axes.unicode_minus']=False
#记录标签对应的位置
def tag(table=None,find=None):
    if(table is None):
        raise 
    length=len(find)
    j=0
    i=0
    c=[]
    while(length>i):
        if(table[j]<find[i]):
            j+=1
        elif(table[j]==find[i]):
            c.append(j)
            #一天内可能有多个买入或卖出原因
            i+=1
        else:
            print(u"表中日期"+str(table[j]) +u",寻找的日期"+str(find[i]))
            raise
    return c
#设置连接数据库的句柄
conn=psql.connect(host='localhost',user='root',password='krvd#l6',port=3306,database='stock',charset='utf8')
cursor=conn.cursor()
#定义相应的类
class candlestickploter:
    def __init__(self,cur,stockindex=0):
    	#获取所有股票的代码
        self.cursor=cur
        self.stockcount=self.cursor.execute("select stockname,MingCheng,LeiBie from XuanZe")
        self.stockcount-=1 #序号从零开始，最后一个比stockcount小，才能保证+1时取到最后一个
        self.stocklist=np.array(self.cursor.fetchall())
        self.stockindex=stockindex
        #绘制第一个图
        self.GetInfo()
        self.fig,(self.ax,self.ax2)=plt.subplots(2,1,sharex=True,gridspec_kw={'height_ratios':[3,1]},figsize=(18,15))
        self.ax.tick_params(length=0)
        self.ax2.set_ylabel('Volume', size=7)
        self.ax2.tick_params(length=0)
        
        self.fig.canvas.mpl_connect('key_press_event', self)
        self.PlotIt()
        plt.show()
        
    def GetInfo(self):
    	#获取所有的历史数据
    	#当某支股票无历史数据时，对其进行忽略，可能有连续多个
        self.Kongji=[]
        while True:
            self.QueryStr="select kaipanjia,shoupanjia,zuigaojia,zuidijia,chengjiaoliang,riqi from " + self.stocklist[self.stockindex][0]
            self.InfoRow=self.cursor.execute(self.QueryStr)
            self.Df=self.cursor.fetchall()
            self.Df=np.array(self.Df)
            if len(self.Df)>0:
                break
            else:
                self.Kongji.append(self.stocklist[self.stockindex][1])
                if self.stockindex<self.stockcount:
                    self.stocklist=np.delete(self.stocklist,self.stockindex,0)
                    self.stockcount-=1
                else:
                	#将字符串列表变成字符串
                    print ",".join(self.Kongji)+u",均为空集，且已到终点\n"
                    raise
                    
        #获取买入日期及原因
        self.QueryStr="select riqi,yuanyin from MaiRuBiao where stockname='" + self.stocklist[self.stockindex][0] + "' order by riqi"
        self.cursor.execute(self.QueryStr)
        self.Buy=np.array(self.cursor.fetchall())
        #当买入数据为空集时，Buy[:,0]出错
        if len(self.Buy)>0:
            self.Buyindex=tag(self.Df[:,5],self.Buy[:,0])
            self.Buy=self.Buy[:,1]
        else:
            self.Buyindex=[]
            self.Buy=[]
        #获取卖出日期及原因
        self.QueryStr="select riqi,yuanyin from MaiChuBiao where stockname='" + self.stocklist[self.stockindex][0] + "' order by riqi"
        self.cursor.execute(self.QueryStr)
        self.Sell=np.array(self.cursor.fetchall())
        #当卖出数据为空集时，Sell[:,0]出错
        if len(self.Sell)>0:
            self.Sellindex=tag(self.Df[:,5],self.Sell[:,0])
            self.Sell=self.Sell[:,1]
        else:
            self.Sellindex=[]
            self.Sell=[]
        #时间间隔导致图中对应的图形之间有间隔
        self.riqi=np.arange(1,1+self.InfoRow)
        #关键点
        self.data=zip(self.riqi,self.Df[:,0],self.Df[:,1],self.Df[:,2],self.Df[:,3])
        self.MA5=pd.rolling_mean(self.Df[:,1],5)
        self.volume =self.Df[:,4]
        self.volume/=np.float32(min(self.volume))
        #出现遗失数据，当开盘价等于收盘价的时候
        self.pos = self.Df[:,0]-self.Df[:,1]<0
        self.neg = self.Df[:,0]-self.Df[:,1]>0
        self.neu=self.Df[:,0]-self.Df[:,1]==0
        
    def PlotIt(self):
        #画图
        self.ax.cla()
        self.ax2.cla()
            
        finan.candlestick_ochl(self.ax,self.data,colorup=u'r',colordown=u'g',alpha=0.5)
        self.ax.set_ylim(min(self.Df[:,3])*0.9,max(self.Df[:,2])*1.1)
        self.ax.plot(self.riqi,self.MA5)
        #标注买入标志
        for xu,index in enumerate(self.Buyindex):
            if xu>0:
                if index==oldindex :
                    LocPlace+=self.Df[index,3]*0.02 
                else:
                    oldindex=index
                    LocPlace=self.Df[index,3]
            else:
                    oldindex=index
                    LocPlace=self.Df[index,3]
            self.ax.text(index,LocPlace,str(self.Buy[xu]),color='b',fontsize=10)
        #标注卖出标志
        for xu,index in enumerate(self.Sellindex):
            if xu>0:
                if index==oldindex :
                    LocPlace+=0.02*self.Df[index,2] 
                else:
                    oldindex=index
                    LocPlace=self.Df[index,2]
            else:
                    oldindex=index
                    LocPlace=self.Df[index,2]
            self.ax.text(index,LocPlace,str(self.Sell[xu]),color='k',fontsize=10)
        if len(self.Kongji)>0:
            self.title=",".join(self.Kongji)+ u" 无历史数据，已跳过\n" +self.stocklist[self.stockindex][1]+" "+ self.stocklist[self.stockindex][2]+" "+str(self.stockindex)
        else:
            self.title=self.stocklist[self.stockindex][1]+" " +self.stocklist[self.stockindex][2]+" "+str(self.stockindex)
        self.fig.suptitle(self.title)
        self.ax2.bar(self.riqi[self.pos],self.volume[self.pos],color='r',width=1,align='center')
        self.ax2.bar(self.riqi[self.neg],self.volume[self.neg],color='g',width=1,align='center')
        self.ax2.bar(self.riqi[self.neu],self.volume[self.neu],color='b',width=1,align='center')

        self.ax2.set_ylim(0,max(self.volume)+1)
        self.ax2.set_xlim(0,self.InfoRow+1)
        self.fig.canvas.draw()       
      
    def __call__(self, event):
        if event.key not in ('a','f'):
            return
        if event.key=='a':
            if self.stockindex>0:
                self.stockindex-=1
                self.GetInfo()
                self.PlotIt()
        elif event.key=='f':
            if self.stockindex<self.stockcount:
                self.stockindex+=1
                self.GetInfo()
                self.PlotIt()
#获得实例
M=candlestickploter(cursor,stockindex=0)          
