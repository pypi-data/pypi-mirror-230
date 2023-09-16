import pandas as pd
import numpy as np
class bars:
	def __init__(self,d,p):
		ohlc = {
			'Open':'first',
			'High':'max',
			'Low':'min',
			'Close':'last'
			}
		self.f = d.resample(p,offset='15min').apply(ohlc)
		self.f.dropna()
		self.f = self.f[
			self.f.Open.notnull() & 
			self.f.High.notnull() & 
			self.f.Low.notnull() & 
			self.f.Close.notnull()
			]
		self.f['avg'] = self.f.iloc[:,1:5].mean(axis=1)
		self.f['d10'] = abs(self.f['avg']-self.f['avg'].shift(10))
		self.f['d01'] = abs(self.f['avg']-self.f['avg'].shift(1))
		self.f['vlt'] = self.f['d01'].rolling(10).sum()
		self.f['efr'] = self.f['d10']/self.f['vlt']
		self.f['sfc'] = ((self.f['efr']*0.6022)-0.0645)**2
		self.f.fillna(0)
		#self.f['sma'] = self.f['avg'].rolling(N).mean()
		h=list(self.f['High'])
		l=list(self.f['Low'])
		a=list(self.f['avg'])
		s=list((self.f['sfc']).fillna(0))	
		self.f['ama']=pd.Series([])
		ama=[]
		ama.append(a[0])
		for i in range (1,len(a)):
			t=(s[i]*a[i]) + (1-s[i])*ama[-1]
			ama.append(t)
			i+=1
		self.f['ama']=ama
		o=list(self.f['avg'])
		c=ama
		minoh=np.minimum(o,c)
		maxoh=np.maximum(o,c)
		h = np.maximum(h,maxoh)
		l = np.minimum(l,minoh)
		self.f['min']=l
		self.f['max']=h
		pass

	def getopen(self):
		return self.f.Open
		pass	
		
	def gethigh(self):
		return self.f.High
		pass	
		
	def getlow(self):
		return self.f.Low
		pass	
		
	def getclose(self):
		return self.f.Close
		pass	

	def getavg(self):
		return self.f['avg']
		pass
	
	def getama(self):
		return self.f['ama']
		pass
	
	def getmin(self):
		return self.f['min']
		pass
	
	def getmax(self):
		return self.f['max']
		pass
				
	def getsma(self,N):
		return (self.f['avg'].rolling(N).mean()).fillna(0)
		pass
			
	def getema(self,s,N):
		k=2/(1+N)
		#s=self.f['avg']
		return s.ewm(alpha=k,adjust=False).mean()
		pass
	
	def gettma(self,s,N):
		k=2/(1+N)
		e1 = self.getema(s,N)
		#print(e1)
		e2 = self.getema(e1,N)
		#print(e2)
		e3 = self.getema(e2,N)
		#print(e3)
		return (3*e1) - (3*e2) + e3
		pass
	pass
