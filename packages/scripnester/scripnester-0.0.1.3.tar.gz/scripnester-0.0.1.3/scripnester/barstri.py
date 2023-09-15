import pandas as pds
import numpy as np
class bars:
	def __init__(self,d,p):
		ohlc = {'Open':'first','High':'max','Low':'min','Close':'last'}
		self.f = d.resample(p,offset='15min').apply(ohlc)
		self.f.dropna()
		self.f = self.f[self.f.Open.notnull() & 
		self.f.High.notnull() & 
		self.f.Low.notnull() & 
		self.f.Close.notnull()]
		self.f['avg'] = self.f.iloc[:,1:5].mean(axis=1)
		self.f['d10'] = abs(self.f['avg']-self.f['avg'].shift(10))
		self.f['d01'] = abs(self.f['avg']-self.f['avg'].shift(1))
		self.f['vlt'] = self.f['d01'].rolling(10).sum()
		self.f['efr'] = self.f['d10']/self.f['vlt']
		self.f['sfc'] = ((self.f['efr']*0.6022)-0.0645)**2
		self.f.fillna(0)
		pass
	
	def getopen(self){
		return self.f.Open
		pass	
		
	def gethigh(self){
		return self.f.Close
		pass	
		
	def getopen(self){
		return self.f.Low
		pass	
		
	def getopen(self){
		return self.f.Close
		pass	


	def getsma(self,N):
		s=self.f['avg']
		return self.f['avg'].rolling(N).mean()
		pass
	
	def getohlcavg(self):
		return list(self.f['avg'])
		pass
	
	def getmin(self):
		o=list(self.f['avg'])
		c=list(getama())
		minoh=np.minimum(_o,_c)
		return minoh
		pass
	
	def getmax(self):
		o=list(self.f['avg'])
		c=list(getama())
		maxoh=np.maximum(_o,_c)
		return maxoh
		pass	

	# a=list
	# s=scaling factor
	def getama(self):
		#a=self.f['avg']
		#s=self.f['sfc']
		a=list((self.f['avg']).fillna(0))
		s=list((self.f['sfc']).fillna(0))	
		#self.f['ama']=pd.Series([])
		ama=[]
		ama.append(a[0])
		for i in range (1,len(a)):
			t=round(
				(s[i]*a[i]) + (1-s[i])*ama[-1],
				2
			)
			ama.append(t)
			i+=1
		return ama
		pass
	
	
	# a=pandas-series
	# N=period
	def getema(self,ps,N):
		s=pd.Series(ps)
		k=2/(1+N)
		ema=round(
			s.ewm(
				alpha=k,
				adjust=False	
			).mean(),
			2
		)
		return ema
		pass
	
	def gettma(self,N):
		s=self.f['avg']
		e1 = self.getema(s,N)
		e2 = self.getema(e1,N)
		e3 = self.getema(e2,N)
		return list((3*e1) - (3*e2) + e3)
		pass


