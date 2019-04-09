# tester.py
# -------
# Tests for regression.py
import regression as r
import databases as d
import time

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
allSharedDates = ['20150521', '20150522', '20150526', '20150527', '20150528', '20150529', '20150601', '20150602',
               '20150603', '20150604', '20150605', '20150608', '20150609', '20150610', '20150611', '20150615',
               '20150616', '20150617', '20150618', '20150619', '20150622', '20150623', '20150624', '20150625',
               '20150629', '20150630', '20150701', '20150702', '20150706', '20150707', '20150708', '20150709',
               '20150713', '20150714', '20150715', '20150716', '20150717', '20150720', '20150721', '20150722',
               '20150723', '20150724', '20150727', '20150728', '20150729', '20150730', '20150731']

"""
Test: famaMacBethRegression8_9 equation 8 functionality
[20150521 - 20150730] Full Sample
[20150521] 1 Day
[20150521 , 20150522] 2 Days
({'a': -0.0011946896272684534, 'b': -0.00944990293514333, 'g1': -0.005327495148892935, 'g2': -0.0033247551604348113, 
'g3': -0.0001189086219906246, 'g4': 2.626995079697868e-05, 'g5': -0.009006338547206236, 'g6': -0.002249047864135485, 
'g7': -0.0018766193849663068, 'g8': -0.0008126018257284923, 'g9': -0.014309528916897891}, 
{'ase': 7.882618293247331e-16, 'bse': 7.803680830760738e-16, 'g1se': 6.208440021695142e-16, 
'g2se': 2.9838434120395265e-16, 'g3se': 1.153232699997732e-18, 'g4se': 1.9675172536251598e-16, 
'g5se': 4.68730234369397e-16, 'g6se': 2.0270305633566148e-16, 'g7se': 1.3740181795044795e-16, 
'g8se': 9.476700517565239e-17, 'g9se': 7.931300478379688e-16})
sharedDates = ['20150521', '20150522']
start = time.time()
print(r.famaMacBethRegression8_9(sharedDates, sharedTics, db, crsp, compustat))
end = time.time()
print(end - start)
"""

"""
Test: famaMacBethRegression8_9 equation 9 functionality
[20150521, 20150522] 2 Days
({'a': 0.26276456584062463, 'b': -0.07394032335972343, 'g1': 0.07140913227288012, 'g2': -0.0368093933889883, 
'g3': -0.001163285910586202, 'g4': 0.027549720180041967, 'g5': 0.04676930382078689, 'g6': -0.011295615213183854, 
'g7': 0.05189593453584103, 'g8': 0.035851676790888506, 'g9': 0.07809399797493781}, 
{'ase': 2.068474535237247e-14, 'bse': 2.4224695045132957e-14, 'g1se': 1.5254050431217347e-14, 
'g2se': 9.028271464969583e-15, 'g3se': 2.579803453681284e-17, 'g4se': 8.45364097203065e-15, 
'g5se': 1.957003443988002e-14, 'g6se': 6.080809275658849e-15, 'g7se': 5.417513647345409e-15, 
'g8se': 3.111852132625305e-15, 'g9se': 3.557511564099966e-14})
sharedDates = ['20150521', '20150522']
start = time.time()
print(r.famaMacBethRegression8_9(sharedDates, sharedTics, db, crsp, compustat, False))
end = time.time()
print(end - start)
"""

"""
Test: famaMacBethRegression10_11 equation 10 functionality
[20150521, 20150522] 2 Days
sharedDates = ['20150521', '20150522']
start = time.time()
print(r.famaMacBethRegression10_11(sharedDates, sharedTics, db, crsp, compustat))
end = time.time()
print(end - start)
"""

"""
Test: famaMacBethRegression10_11 equation 11 functionality
[20150521, 20150522] 2 Days
sharedDates = ['20150521', '20150522']
start = time.time()
print(r.famaMacBethRegression10_11(sharedDates, sharedTics, db, crsp, compustat, False))
end = time.time()
print(end - start)
"""

"""
Test: famaMacBethRegression10_11 equation 11 functionality
[20150521, 20150522] 2 Days t1:2 t2:4
[20150521, 20150522] 2 Days t1:2 t2:6
[20150521, 20150522] 2 Days t1:2 t2:11
sharedDates = ['20150521', '20150522']
t1 = 2
t2 = 11
start = time.time()
print(r.famaMacBethRegression12(sharedDates, sharedTics, db, crsp, compustat, t1, t2))
end = time.time()
print(end - start)
"""





