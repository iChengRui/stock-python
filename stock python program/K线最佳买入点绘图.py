#导入相关库
import matplotlib.pyplot as plt
import matplotlib.finance as finan
import pandas as pd
import numpy as np
import pymysql as psql
#设置，让中文正常显示
plt.rcParams['font.sans-serif']=['Microsoft YaHei']
plt.rcParams['axes.unicode_minus']=False
#标记理想的买入点 函数
def tag(riqi,data,lastDay=5,durationLoss=0.03,minIncrease=0.05):
    length=len(data)
    i=0
    c=[]
    while(i<length):
        j=1
        while(j<lastDay and j+i<length):
            if data[i]*(1+minIncrease)<=data[i+j] :
                #注意日期没有0，不能使用索引i进行单纯的替换
                c.append(riqi[i])
                break
            elif data[i]*(1-durationLoss)>data[i+j]:
                break
            else:
                pass
            j+=1
        i+=1      
    return c
#连接数据库
conn=psql.connect(host='localhost',user='root',password='krvd#l6',port=3306,database='stock',charset='utf8')
cursor=conn.cursor()
stockcount=cursor.execute("select stockname,MingCheng,LeiBie from XuanZe")
stocklist=cursor.fetchall()
#定义绘图的类
class candlestickploter:
    def __init__(self,cur,stockindex=0):
    	#获取所有股票的代码
        self.cursor=cur
        self.stockcount=self.cursor.execute("select stockname,MingCheng,LeiBie from XuanZe")
        self.stocklist=self.cursor.fetchall()
        self.stockindex=stockindex
        #绘制第一个图
        self.GetInfo()
        self.fig,(self.ax,self.ax2,self.ax3)=plt.subplots(3,1,sharex=True,gridspec_kw={'height_ratios':[2,1,1]},figsize=(18,15))
        self.ax.tick_params(length=0)
        self.ax2.set_ylabel('Volume', size=7)
        self.ax2.tick_params(length=0)
        
        self.fig.canvas.mpl_connect('key_press_event', self)
        self.PlotIt()
        plt.show()
        
    def GetInfo(self):
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
                    print ",".join(self.Kongji)+",all is empty set,jump\n"
                    raise
        #时间间隔导致图中对应的图形之间有间隔
        self.riqi=np.arange(1,1+self.InfoRow)
        #关键点
        self.data=zip(self.riqi,self.Df[:,0],self.Df[:,1],self.Df[:,2],self.Df[:,3])
        self.MA3=pd.rolling_mean(self.Df[:,1],3)
        self.MA5=pd.rolling_mean(self.Df[:,1],11)
        self.volume =self.Df[:,4]
        self.volume/=min(self.volume)
        #出现遗失数据，当开盘价等于收盘价的时候
        self.pos = self.Df[:,0]-self.Df[:,1]<0
        self.neg = self.Df[:,0]-self.Df[:,1]>0
        self.neu=self.Df[:,0]-self.Df[:,1]==0

        self.TagIndex=tag(self.riqi,self.Df[:,1])
        self.TagY=np.ones(len(self.TagIndex))*(self.Df[:,3].min()*0.95)
        
    def PlotIt(self):
        #画图
        self.ax.cla()
        self.ax2.cla()
        self.ax3.cla()
            
        finan.candlestick_ochl(self.ax,self.data,colorup=u'r',colordown=u'g',alpha=0.5)
        #self.ax.plot(self.riqi,self.MA3)
        self.ax.plot(self.TagIndex,self.TagY,'y^')
        
        if len(self.Kongji)>0:
            self.title=",".join(self.Kongji)+ u" 无历史数据，已跳过\n" +self.stocklist[self.stockindex][1]+" "+ self.stocklist[self.stockindex][2]+" "+str(self.stockindex)
        else:
            self.title=self.stocklist[self.stockindex][1]+" " +self.stocklist[self.stockindex][2]+" "+str(self.stockindex)
        self.fig.suptitle(self.title)
       
        
        self.ax2.bar(self.riqi[self.pos],self.volume[self.pos],color='r',width=1,align='center')
        self.ax2.bar(self.riqi[self.neg],self.volume[self.neg],color='g',width=1,align='center')
        self.ax2.bar(self.riqi[self.neu],self.volume[self.neu],color='b',width=1,align='center')

        self.ax2.set_ylim(0,max(self.volume)+1)
        
        self.ax3.plot(self.riqi,self.MA5,'r-',self.riqi,self.MA3,'g-')
        self.ax3.set_xlim(0,1+self.InfoRow)

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
#绘图的实例
M=candlestickploter(cursor,stockindex=53)
