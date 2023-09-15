class token:
	def __init__(self,df,trend,ltp,symbol):
		self.df=df
		self.trend=trend
		self.ltp=ltp
		self.symbol=symbol			
	
	def trendup(self):
		strike_above = int((self.ltp+50)/50)*50
		strike = str(strike_above)+"-CE"
		return self.df.loc[self.df.SEM_TRADING_SYMBOL.str.endswith(strike),:]
	
	def trendown(self):
		strike_below = (int((self.ltp+50)/50)*50)-50
		strike = str(strike_below)+"-PE"
		return(self.df.loc[self.df.SEM_TRADING_SYMBOL.str.endswith(strike),:])
	
	def trendfut(self):
		return self.df.loc[self.df.SEM_TRADING_SYMBOL.str.startswith(self.symbol),:]
		
	def getsecid(self): 
		if(self.trend=='up'):
			return (self.trendup().iloc[0,2:3]).to_numpy()[0]
		elif(self.trend=='down'):
			return (self.trendown().iloc[0,2:3]).to_numpy()[0]	
		elif(self.trend=='fut' and self.symbol != ""):
			return (self.trendfut().iloc[0,2:3]).to_numpy()[0]
		else:
			return 'no'

	pass
