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

"""
Test: famaMacBethRegression8 functionality
[20150521 - 20150730] Full Sample
({'a': -0.016836920345238343, 'b': -0.007082890955078101, 'g1': 0.013917343741111086, 'g2': -0.010184097896666765, 
'g3': 2.4239509588612176e-05, 'g4': 0.002127772319503965, 'g5': -0.006335526618678873, 'g6': 0.14226578209832283, 
'g7': 0.3739440086596395, 'g8': 0.4660566567676302, 'g9': 0.006321780178858654},
 {'ase': 0.005772190548570919, 'bse': 0.0003585272973961142, 'g1se': 0.0005684657776585838, 
 'g2se': 0.002525924842002543, 'g3se': 1.248273530273534e-06, 'g4se': 0.00032612746362372644, 
 'g5se': 0.0006750243323908417, 'g6se': 0.012573246369229157, 'g7se': 0.08220790087614971, 
 'g8se': 0.057700433190975446, 'g9se': 0.0005029621478354697})
[20150521 , 20150522] 1 Day
({'a': -0.0034101166708870034, 'b': -0.01843736557065106, 'g1': -0.010654682293966895, 'g2': -0.006701822965388907, 
'g3': 6.896700570472351e-05, 'g4': -0.007594418789522064, 'g5': -0.01721832101183742, 'g6': -0.004480788308241562, 
'g7': -0.003865690346330424, 'g8': -0.0018159950060968393, 'g9': -0.03183571394146708}, 
{'ase': 1.950058950595755e-15, 'bse': 1.4266642786125925e-15, 'g1se': 6.760902824318515e-16, 
'g2se': 5.771224738172824e-16, 'g3se': 1.1299004677633281e-18, 'g4se': 2.912660555082555e-16, 
'g5se': 6.061201704575776e-16, 'g6se': 3.402100480155517e-16, 'g7se': 3.0082503326011166e-16, 
'g8se': 2.1091422792070395e-16, 'g9se': 1.0608107096786021e-15})
['20150521' - '20150526'] 2 Days
({'a': -0.0015170749692255598, 'b': -0.009218682785325564, 'g1': -0.005139357780765608, 'g2': -0.0032360662812467985, 
'g3': -0.00011939407962051235, 'g4': 4.695248810642665e-05, 'g5': -0.008967903417169784, 'g6': -0.002182351562233112, 
'g7': -0.0019228436449183588, 'g8': -0.0009017795034672995, 'g9': -0.01428856754974274}, 
{'ase': 9.750294845935269e-16, 'bse': 7.133321393062962e-16, 'g1se': 3.380451680275281e-16,
'g2se': 2.8856124864335086e-16, 'g3se': 5.825395349848871e-19, 'g4se': 1.4565904647430257e-16, 
'g5se': 3.030601942675734e-16, 'g6se': 1.7010502909298193e-16, 'g7se': 1.504125168007829e-16, 
'g8se': 1.0545711405444639e-16, 'g9se': 5.304066408166379e-16})
--- 2 Days After Optimization 1
({'a': -0.0016013579333896072, 'b': -0.00919955038911061, 'g1': -0.005156822484945728, 'g2': -0.003226090394722654,
 'g3': -0.0001193825055448252, 'g4': 4.191634706213502e-05, 'g5': -0.008988386704852339, 'g6': -0.0021790195898092396, 
 'g7': -0.00194050457153743, 'g8': -0.00018558380862437494, 'g9': -0.014322541048448652}, 
{'ase': 1.5322225703760403e-15, 'bse': 1.2905009353409248e-15, 'g1se': 8.062404965546405e-16, 
'g2se': 5.084769384227704e-16, 'g3se': 1.3574468215305422e-18, 'g4se': 2.9083775974222507e-16, 
'g5se': 6.511601889813905e-16, 'g6se': 3.207173186665871e-16, 'g7se': 2.4015564265493607e-16, 
'g8se': 3.5930205525497436e-17, 'g9se': 1.1165876626405327e-15})
----- 2 Days After Optimization 2
({'a': -0.0016013579333893383, 'b': -0.009199550389110876, 'g1': -0.00515682248494575, 'g2': -0.0032260903947227662,
 'g3': -0.00011938250554482637, 'g4': 4.191634706210423e-05, 'g5': -0.008988386704852436, 'g6': -0.0021790195898092938,
  'g7': -0.001940504571537408, 'g8': -0.00018558380862436957, 'g9': -0.01432254104844871}, 
{'ase': 3.2652277681876203e-16, 'bse': 2.572405424384062e-16, 'g1se': 1.9478349115098893e-16,
 'g2se': 1.0038622181723986e-16, 'g3se': 6.533204257987668e-19, 'g4se': 8.363713592829991e-17, 
 'g5se': 1.9906682906677425e-16, 'g6se': 6.176638210144283e-17, 'g7se': 7.145627387840913e-17, 
 'g8se': 9.411246257902279e-18, 'g9se': 3.5145383052117863e-16})
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
sharedDates = ['20150521', '20150522', '20150526']
start = time.time()
print(r.famaMacBethRegression8(sharedDates, sharedTics, db, crsp, compustat))
end = time.time()
print(end - start)
