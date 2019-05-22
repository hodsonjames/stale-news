# process_market_tester.py
# -------
# Tests for databases.py ProcessedMarketDatabase
import databases as d

mdb = d.ProcessedMarketDatabase("../market_measures.csv")
"""
dict_ar = mdb.abn_ret["AAPL"]
for k in dict_ar:
    print(k, dict_ar[k])
"""
print("Expected: -0.00912777688 Actual: " + str(mdb.abnormalReturn("AAPL", "20181231", -5, -1)))
print("Expected: -0.04443402413 Actual: " + str(mdb.abnormalReturn("AAPL", "20000410", -5, -1)))


"""
dict_av = mdb.abn_vol["AAPL"]
for k in dict_av:
    print(k, dict_av[k])
"""
print("Expected: 0.00303392624 Actual: " + str(mdb.abnormalVol("AAPL", "20181231", -5, -1)))
print("Expected: 0.01266838288 Actual: " + str(mdb.abnormalVol("AAPL", "20000410", -5, -1)))


"""
dict_ill = mdb.illiq["AAPL"]
for k in dict_ill:
    print(k, dict_ill[k])
"""
print("Expected: -8.42723836098 Actual: " + str(mdb.illiquidity("AAPL", "20181231", -5, -1)))
print("Expected: -4.58696673867 Actual: " + str(mdb.illiquidity("AAPL", "20000410", -5, -1)))


"""
dict_avo = mdb.abn_volat["AAPL"]
for k in dict_avo:
    print(k, dict_avo[k])
"""
print("Expected: 0.01238832405 Actual: " + str(mdb.abnormalVolatility("AAPL", "20181231", -5, -1)))
print("Expected: 0.03561621697 Actual: " + str(mdb.abnormalVolatility("AAPL", "20000410", -5, -1)))

