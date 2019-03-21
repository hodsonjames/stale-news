# tester.py
# -------
# Tests for regression.py
import regression as r
import databases as d

# setup databases to read in from
compustat = d.PandasDatabase("compustatQ.csv")
crsp = d.CRSPDatabase("crspdaystock.csv")
crspmini = d.CRSPDatabase("crspdaystockmini.csv")
db = d.MeasuresDatabase("simulated_data.txt")
print("SETUP DONE")
"""
Find shared firms between databases
compustat.recordTickers("tic", False)
crsp.recordTickers("TICKER", False)
sharedTics = set(compustat.tics) & set(crsp.tics) & set(db.tics.keys())
sharedTics = list(sharedTics)
"""
"""
Find shared dates between crsp and measures databases
crsp.recordDates("date", False)
unsynced = []
sharedDates = (set(map(str, crsp.dates)) & set(db.dates.keys())) - set(unsynced)
sharedDates = list(sharedDates)
sharedDates.sort()
print(sharedDates)
"""

"""
Test: famaMacBethRegression8 functionality
[20150521 , 20150730]
{'a': -0.0168369203452307, 'b': -0.007082890955080441, 'g1': 0.013917343741098648, 'g2': -0.01018409789665938, 
'g3': 2.423950958859024e-05, 'g4': 0.0021277723195040547, 'g5': -0.00633552661868291, 'g6': 0.14226578209833188, 
'g7': 0.37394400865957245, 'g8': 0.46605665676775965, 'g9': 0.006321780178857675}
"""
sharedTics = ['WBA', 'WETF', 'LL', 'ADVS', 'CME', 'CI', 'UPS', 'FIS', 'TRN', 'FDX', 'WMT', 'BA', 'MTB', 'EXC', 'RTN',
              'OI', 'SRCL', 'CELG', 'CG', 'MGM', 'DE', 'UAL', 'PRU', 'MON', 'VIAB', 'HLT', 'ABT', 'FOXA', 'FCX', 'GFIG',
              'VZ', 'GNW', 'HAL', 'RAI', 'CAG', 'M', 'SBUX', 'DAL', 'DLR', 'NFLX', 'DHR', 'AMGN', 'SF', 'AVGO', 'PFE',
              'PM', 'CCI', 'PG', 'MS', 'YUM', 'KHC', 'LLY', 'NKE', 'NXPI', 'AER', 'V', 'TXN', 'MU', 'SYY', 'WLL', 'XOM',
              'CBS', 'JNJ', 'CTXS', 'PRGO', 'TRCO', 'IEP', 'COST', 'BIIB', 'PETC', 'AAPL', 'MO', 'QRVO', 'TGNA', 'MMM',
              'HUM', 'MYL', 'BHI', 'AMAT', 'WFM', 'BGCP', 'DIS', 'ATI', 'VRSK', 'UTX', 'TMUS', 'PLL', 'PCG', 'MSFT',
              'MET', 'PXD', 'AVP', 'F', 'MMS', 'CAT', 'HES', 'ENDP', 'INTC', 'GS', 'BX', 'BGC', 'HCBK', 'SLXP', 'NDAQ',
              'PYPL', 'APA', 'KR', 'OLN', 'PEP', 'MCD', 'CHTR', 'SPG', 'GCI', 'CNC', 'HRC', 'HPQ', 'LOW', 'UNH', 'LC',
              'PSX', 'AGN', 'WPX', 'NYT', 'MCK', 'DLTR', 'HON', 'FB', 'YELP', 'OVTI', 'ZTS', 'OMF', 'GEVA', 'T', 'ALT',
              'SNAP', 'EMC', 'ADP', 'COP', 'STE', 'ANTM', 'DOW', 'LNKD', 'JCI', 'QCOM', 'ARRS', 'GOOGL', 'OCN', 'MPC',
              'BBY', 'GE', 'NE', 'ARES', 'GGP', 'ALTR', 'AA', 'AIG', 'JPM', 'AAL', 'ALL', 'BMY', 'ORCL', 'VIRT', 'KKR',
              'AXP', 'CMCSA', 'LUV', 'MA', 'AMZN', 'OB', 'ARCC', 'WU', 'OXY', 'LAUR', 'EBAY', 'SPB', 'CSCO', 'GLPI',
              'KO', 'DD', 'SWKS', 'JACK', 'BLDR', 'LO', 'MRK', 'SPRD', 'CVX', 'MSI', 'FIT', 'EIGI', 'DISH', 'ARNC',
              'THOR', 'OCR', 'HMSY', 'BLK', 'ABBV', 'ESRX', 'NSM', 'UDR', 'BAC', 'SYMC', 'S', 'COTY', 'OPK', 'XPO',
              'ALXN', 'WTM', 'CRM', 'STJ', 'MGI', 'BBT', 'NFBK', 'MAC', 'AET', 'HIG', 'C', 'HD', 'FCAU', 'EPD', 'ALLY',
              'TSLA', 'LIVN', 'TGT', 'AAP', 'ICE', 'CAH', 'TWTR', 'BABA', 'APO', 'IBM', 'CVS', 'JBLU', 'GM', 'GILD',
              'ZNGA', 'WFC']
sharedDates = ['20150521', '20150522', '20150526', '20150527', '20150528', '20150529', '20150601', '20150602',
               '20150603', '20150604', '20150605', '20150608', '20150609', '20150610', '20150611', '20150615',
               '20150616', '20150617', '20150618', '20150619', '20150622', '20150623', '20150624', '20150625',
               '20150629', '20150630', '20150701', '20150702', '20150706', '20150707', '20150708', '20150709',
               '20150713', '20150714', '20150715', '20150716', '20150717', '20150720', '20150721', '20150722',
               '20150723', '20150724', '20150727', '20150728', '20150729', '20150730', '20150731']
print(r.famaMacBethRegression8(sharedDates, sharedTics, db, crsp, compustat))


