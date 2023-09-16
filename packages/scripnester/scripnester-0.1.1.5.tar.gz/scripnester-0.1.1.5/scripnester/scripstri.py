import pandas as pd
class scrips:
	def __init__(self, path, previous_close, targetday):
		self.above=float(previous_close+300)
		self.below=float(previous_close-300)
		self.df=pd.read_csv(path)
		self.exdf=self.df.loc[self.df.SEM_EXM_EXCH_ID.str.contains('NSE'),:]
		#print(self.exdf)
		#self.oidf=self.exdf.query(SEM_INSTRUMENT_NAME == @'OPTIDX' & SEM_EXPIRY_DATE in @targetday & SEM_STRIKE_PRICE < @self.above & SEM_STRIKE_PRICE > @self.below') 
		#self.copt=self.oidf.query('SEM_OPTION_TYPE== @_ce')
		#self.popt=self.oidf.query('SEM_OPTION_TYPE== @_pe')
		self.oidf=self.exdf.loc[self.exdf.SEM_INSTRUMENT_NAME.str.contains('OPTI\w+'),:]
		self.oit=self.oidf.query('SEM_EXPIRY_DATE in @targetday & SEM_STRIKE_PRICE < @self.above & SEM_STRIKE_PRICE > @self.below')
		self.ces=self.oit.loc[self.oit.SEM_OPTION_TYPE.str.contains('CE'),:]
		self.pes=self.oit.loc[self.oit.SEM_OPTION_TYPE.str.contains('PE'),:]
		#print(self.oit)
		#print(self.ces)
		#print(self.pes)
		
		self.fidf=self.exdf.loc[self.exdf.SEM_INSTRUMENT_NAME.str.contains('FUTI\w+'),:]
		#print(self.fidf)
	
	def getalphap(self): return self.pes
		
	def getalphac(self): return self.ces
	
	def getalphaf(self): return self.fidf
	
	
	pass
