# tester.py
# -------
# Unit and integration tests for databases.py, utils.py
import databases as d
import utils as u
import time

# setup databases to read in from
compustat = d.PandasDatabase("compustatQ.csv")
crsp = d.CRSPDatabase("crspdaystock.csv")
crspmini = d.CRSPDatabase("crspdaystockmini.csv")
db = d.MeasuresDatabase("simulated_data.txt")
print("SETUP DONE")

"""
Test: PandasDatabase data overview
print("COMPUSTAT: ")
print(list(compustat.data))
print(compustat.data.dtypes)
print(compustat.data.tail(5))
print("CRSP: ")
print(list(crsp.data))
print(crsp.data.dtypes)
print(crsp.data.tail(5))
"""

"""
Test: PandasDatabase data basic queries
print("COMPUSTAT: ")
print(compustat.data['ceqq'])
print("CRSP: ")
print(crsp.data['RETX'])
"""

"""
Test: PandasDatabase tics functionality
crsp.recordTickers("TICKER")
print(crsp.tics)
compustat.recordTickers("tic")
print(compustat.tics)
"""

"""
Test: PandasDatabase dates functionality
crsp.recordDates("date")
print(crsp.dates)
compustat.recordDates("datadate")
print(compustat.dates)
"""

"""
Test: MeasuresDatabase tdMap functionality
count = 0
for k in db.tdMap:
    print("TICKER: " + k[0] + " DATE: " + k[1])
    for row in db.tdMap.get(k):
        print(row)
        count += 1
print(count)
"""

"""
Test: MeasuresDatabase dates functionality
count = 0
for k in db.dates:
    print("DATE: " + k)
    count += 1
print(count)
"""

"""
Test: MeasuresDatabase tics functionality
count = 0
# out = ""
for k in db.tics:
    print("TIC: " + k)
    # out += k + " "
    count += 1
# print(out)
print(count)
"""

"""
Test: TextDatabase getMatches functionality
matches = db.getMatches("WHAM6K50YV", 0)
print("ARTICLE: WHAM6K50YV")
for m in matches:
    print(m)
matches = db.getMatches("6AD46K50Y0", 0)
print("ARTICLE: 6AD46K50Y0")
for m in matches:
    print(m)
"""

"""
Test: percentageOld functionality 
print("Expected: 0.5 Actual: " + str(u.percentageOld("PRGO", "20150421", db)))
print("Expected: -1 Actual: " + str(u.percentageOld("PRGO", "2015042", db)))
print("Expected: -1 Actual: " + str(u.percentageOld("FAKE", "20150421", db)))
"""

"""
Test: percentageRecombinations functionality 
print("Expected: 0.5 Actual: " + str(u.percentageOld("PRGO", "20150421", db)))
print("Expected: 1.0 Actual: " + str(u.percentageOld("MSFT", "20150416", db)))
print("Expected: -1 Actual: " + str(u.percentageOld("PRGO", "2015042", db)))
print("Expected: -1 Actual: " + str(u.percentageOld("FAKE", "20150421", db)))
"""

"""
Test: stories functionality
print("Expected: 2 Actual: " + str(u.stories("PRGO", "20150421", db)))
print("Expected: 2 Actual: " + str(u.stories("TWTR", "20150611", db)))
print("Expected: 0 Actual: " + str(u.stories("DOES NOT EXIST", "20150611", db)))
print("Expected: 0 Actual: " + str(u.stories("TWTR", "302123231", db)))
"""

"""
Test: terms functionality
print("Expected: 208.5 Actual: " + str(u.terms("PRGO", "20150421", db)))
print("Expected: 97.0 Actual: " + str(u.terms("TWTR", "20150611", db)))
print("Expected: -1 Actual: " + str(u.terms("DOES NOT EXIST", "20150611", db)))
print("Expected: -1 Actual: " + str(u.terms("TWTR", "302123231", db)))
"""

"""
Test: abnormalStories functionality
print("Expected: -1 Actual: " + str(u.abnormalStories("PRGO", "20150421", db)))
start = time.time()
print("Expected: 0.32727272727272727 Actual: " + str(u.abnormalStories("FCAU", "20150730", db)))
print("Expected: -0.07272727272727272 Actual: " + str(u.abnormalStories("AAPL", "20150721", db)))
end = time.time()
print("Time elapsed: " + str(end - start))
"""

"""
Test: abnormalPercentageOld functionality
tickers = list(db.tics.keys())
for t in tickers:
    if (t, "20150421") in db.tdMap:
        print(t + " AbnPctOld: " + str(u.abnormalPercentageOld(t, "20150421", db)) + "  PctOld: " + str(u.percentageOld(t, "20150421", db)))
"""

"""
Test: abnormalPercentageOld functionality
tickers = list(db.tics.keys())
start = time.time()
for t in tickers:
    if (t, "20150421") in db.tdMap:
        print(t + " AbnPctOld: " + str(u.abnormalPercentageOld(t, "20150421", db)) + "  PctOld: " + str(u.percentageOld(t, "20150421", db)))
end = time.time()
print("Time elapsed: " + str(end - start))
"""

"""
Test: abnormalPercentageRecombinations functionality
tickers = list(db.tics.keys())
start = time.time()
for t in tickers:
    if (t, "20150423") in db.tdMap:
        print(t + " AbnPctRecombinations: " + str(u.abnormalPercentageRecombinationsParallel(t, "20150423", db)) + "  PctRecombinations: " + str(u.percentageRecombinations(t, "20150423", db)))
end = time.time()
print("Time elapsed: " + str(end - start))
"""

"""
Test: firmReturn functionality
verbose = False
firm = "ORCL"
date = "20000103"
if verbose:
    print(crsp.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")'))
print("Expected: 0.054099 Actual: " + str(u.firmReturn(firm, date, crsp)))
firm2 = "TSLA"
date2 = "20181231"
if verbose:
    print(crsp.data.query('(TICKER == "' + firm2 + '") & (date == "' + date2 + '")'))
print("Expected: -0.003205 Actual: " + str(u.firmReturn(firm2, date2, crsp)))
firm3 = "AAPL"
date3 = "20000103"
if verbose:
    print(crsp.data.query('(TICKER == "' + firm3 + '") & (date == "' + date3 + '")'))
print("Expected: 0.088754 Actual: " + str(u.firmReturn(firm3, date3, crsp)))
firm4 = "TSLA"
date4 = "20000103"
print("Expected -1 Actual: " + str(u.firmReturn(firm4, date4, crsp)))
"""

"""
Test: allFirmsReturn functionality
verbose = False
date = "20000103"
if verbose:
    print(crsp.data.query('date == "' + date + '"'))
print("Expected: -0.006817 Actual: " + str(u.allFirmsReturn(date, crsp)))
date2 = "20000118"
if verbose:
    print(crsp.data.query('date == "' + date2 + '"'))
print("Expected: -0.000874 Actual: " + str(u.allFirmsReturn(date2, crsp)))
date3 = "20181231"
if verbose:
    print(crsp.data.query('date == "' + date3 + '"'))
print("Expected: 0.008107 Actual: " + str(u.allFirmsReturn(date3, crsp)))
date4 = "19991220"
print("Expected: -1 Actual: " + str(u.allFirmsReturn(date4, crsp)))
"""

"""
Test: abnormalReturnDate functionality
firm = "ORCL"
date = "20000103"
print("Expected: 0.060916 Actual: " + str(u.abnormalReturnDate(firm, date, crsp)))
firm = "TSLA"
date = "20181231"
print("Expected: -0.011312 Actual: " + str(u.abnormalReturnDate(firm, date, crsp)))
firm = "TSLA"
date = "19991231"
print("Expected: -1 Actual: " + str(u.abnormalReturnDate(firm, date, crsp)))
"""

"""
Test: abnormalReturn functionality
firm = "ORCL"
dateStart = "20150224"
dateEnd = "20150226"
start = time.time()
print("Expected: 0.001395 Actual: " + str(u.abnormalReturn(firm, dateStart, dateEnd, crsp)))
end = time.time()
print("Time elapsed small: " + str(end - start))
firm = "TSLA"
dateStart = "20150717"
dateEnd = "20150731"
start = time.time()
print("Expected: 0.014217 Actual: " + str(u.abnormalReturn(firm, dateStart, dateEnd, crsp)))
end = time.time()
print("Time elapsed larger: " + str(end - start))
firm = "TSLA"
dateStart = "20000103"
dateEnd = "20150731"
# date range will not occur in practice, can add extra checks in function to make this fast
print("Expected: -1 Actual: " + str(u.abnormalReturn(firm, dateStart, dateEnd, crsp)))
"""

"""
Test: marketCap functionality
firm = "ORCL"
date = "20000103"
print("Expected: 177425123000.0 Actual: " + str(u.marketCap(firm, date, crsp)))
firm2 = "TSLA"
date2 = "20181231"
print("Expected: 58009691787.33 Actual: " + str(u.marketCap(firm2, date2, crsp)))
firm3 = "TSLA"
date3 = "20000103"
print("Expected -1 Actual: " + str(u.marketCap(firm3, date3, crsp)))
"""

"""
Test: marketCapLN functionality
firm = "ORCL"
date = "20000103"
print("Expected: 25.9018145146 Actual: " + str(u.marketCapLN(firm, date, crsp)))
firm2 = "TSLA"
date2 = "20181231"
print("Expected: 24.7838759333 Actual: " + str(u.marketCapLN(firm2, date2, crsp)))
firm3 = "TSLA"
date3 = "20000103"
print("Expected -1 Actual: " + str(u.marketCapLN(firm3, date3, crsp)))
"""

"""
Test: totalMarketCap functionality
mini = False
if mini:
    date = "20000216"
    print("Expected: 36403372125.0 Actual: " + str(u.totalMarketCap(date, crspmini)[0]))
    date = "20181231"
    print("Expected: 1262719025820.0 Actual: " + str(u.totalMarketCap(date, crspmini)[0]))
else:
    # tests take longer than usual to run, as there is no benefit of cached data without many queries
    date = "20000103"
    start = time.time()
    print("Expected: 7550986428771.2 Actual: " + str(u.totalMarketCap(date, crsp)[0]))
    end = time.time()
    print("Time one operation: " + str(end - start))
    print("Expected: 7550986428771.2 Saved Actual: " + str(u.totalMarketCap(date, crsp)[0]))
    date = "20181231"
    print("Expected: 14718446746677.063 Actual: " + str(u.totalMarketCap(date, crsp)[0]))
    date = "10181231"
    print("Expected: -1 Actual: " + str(u.totalMarketCap(date, crsp)[0]))
"""

"""
Test: firmVolume functionality
verbose = False
firm = "ORCL"
date = "20000103"
if verbose:
    print(crsp.data.query('(TICKER == "' + firm + '") & (date == "' + date + '")'))
print("Expected: 24831819.0 Actual: " + str(u.firmVolume(firm, date, crsp)))
firm2 = "TSLA"
date2 = "20181231"
if verbose:
    print(crsp.data.query('(TICKER == "' + firm2 + '") & (date == "' + date2 + '")'))
print("Expected: 6302338.0 Actual: " + str(u.firmVolume(firm2, date2, crsp)))
firm3 = "TSLA"
date3 = "20000103"
print("Expected -1 Actual: " + str(u.firmVolume(firm3, date3, crsp)))
"""

"""
Test: firmVolumeFrac functionality
firm = "ORCL"
date = "20000103"
print("Expected: 0.0174420927011 Actual: " + str(u.firmVolumeFrac(firm, date, crsp)))
firm2 = "TSLA"
date2 = "20181231"
print("Expected: 0.0366984679706 Actual: " + str(u.firmVolumeFrac(firm2, date2, crsp)))
firm3 = "TSLA"
date3 = "20000103"
print("Expected -1 Actual: " + str(u.firmVolumeFrac(firm3, date3, crsp)))
firm4 = "ORCL"
date4 = "20181231"
print("Expected 0.00416076567 Actual: " + str(u.firmVolumeFrac(firm4, date4, crspmini)))
firm5 = "HON"
date5 = "20000216"
print("Expected 0.00345778749 Actual: " + str(u.firmVolumeFrac(firm5, date5, crspmini)))
"""

"""
Test: allFirmsVolumeFrac functionality
mini = False
if mini:
    date = "20181231"
    print("Expected: 0.0058174855 Actual: " + str(u.allFirmsVolumeFrac(date, crspmini)))
    date = "20000216"
    print("Expected: 0.00345778749 Actual: " + str(u.allFirmsVolumeFrac(date, crspmini)))
else:
    # tests take longer than usual to run, as there is no benefit of cached data without many queries
    date = "20000103"
    start = time.time()
    print("Output: " + str(u.allFirmsVolumeFrac(date, crsp)))
    end = time.time()
    print("Time elapsed: " + str(end - start))
    print("Saved Output: " + str(u.allFirmsVolumeFrac(date, crsp)))
    date = "20181231"
    print("Output: " + str(u.allFirmsVolumeFrac(date, crsp)))
    date = "10181231"
    print("Expected: -1 Actual: " + str(u.allFirmsVolumeFrac(date, crsp)))
"""

"""
Test: abnormalVolDate functionality
mini = False
if mini:
    firm = "ORCL"
    date = "20181231"
    print("Expected -0.00165671983 Actual: " + str(u.abnormalVolDate(firm, date, crspmini)))
    firm = "HON"
    date = "20000216"
    print("Expected 0.0 Actual: " + str(u.abnormalVolDate(firm, date, crspmini)))
else:
    # tests take longer than usual to run, as there is no benefit of cached data without many queries
    firm = "ORCL"
    date = "20000103"
    print("Expected: 0.01053044341 Actual:" + str(u.abnormalVolDate(firm, date, crsp)))
    firm = "FAKE"
    date = "10181231"
    print("Expected: -1 Actual:" + str(u.abnormalVolDate(firm, date, crsp)))
"""

"""
Test: abnormalVol functionality
mini = False
if mini:
    firm = "ORCL"
    dateStart = "20181231"
    dateEnd = "20181231"
    print("Expected -0.00165671983 Actual: " + str(u.abnormalVol(firm, dateStart, dateEnd, crspmini)))
    firm = "ORCL"
    dateStart = "20181228"
    dateEnd = "20181231"
    print("Expected 0.00137226214 Actual: " + str(u.abnormalVol(firm, dateStart, dateEnd, crspmini)))
else:
    # tests will take a while to run, as there is no benefit of cached data without many queries
    firm = "ORCL"
    dateStart = "20150223"
    dateEnd = "20150227"
    start = time.time()
    print("Output: " + str(u.abnormalVol(firm, dateStart, dateEnd, crsp)))
    end = time.time()
    print("Time elapsed: " + str(end - start))
    firm = "TSLA"
    dateStart = "20000103"
    dateEnd = "20150731"
    # date range will not occur in practice, can add extra checks in PARALLEL function version to make this fast
    print("Expected: -1 Actual: " + str(u.abnormalVol(firm, dateStart, dateEnd, crsp)))
"""

"""
Test: abnormalVolatilityDate functionality
firm = "ORCL"
date = "20000131"
start = time.time()
print("Expected: 0.04742965 Actual: " + str(u.abnormalVolatilityDate(firm, date, crsp)))
end = time.time()
print("Time elapsed: " + str(end - start))
firm = "MSFT"
date = "20181231"
print("Expected: 0.01184607 Actual: " + str(u.abnormalVolatilityDate(firm, date, crsp)))
firm = "FAKE"
date = "20000201"
print("Expected: -1 Actual: " + str(u.abnormalVolatilityDate(firm, date, crsp)))
firm = "ORCL"
date = "20000201"
print("Output: " + str(u.abnormalVolatilityDate(firm, date, crsp)))
"""

"""
Test: abnormalVolatility functionality
firm = "ORCL"
dateStart = "20000131"
dateEnd = "20000204"
start = time.time()
print("Output: " + str(u.abnormalVolatility(firm, dateStart, dateEnd, crsp)))
end = time.time()
print("Time elapsed: " + str(end - start))
firm = "ORCL"
dateStart = "20000131"
dateEnd = "20000131"
print("Expected: 0.04742965 Actual: " + str(u.abnormalVolatility(firm, dateStart, dateEnd, crsp)))
firm = "ORCL"
dateStart = "20000131"
dateEnd = "20000201"
print("Expected: 0.04770185327 Actual: " + str(u.abnormalVolatility(firm, dateStart, dateEnd, crsp)))
firm = "TSLA"
dateStart = "20100629"
dateEnd = "20181231"
print("Expected: -1 Actual: " + str(u.abnormalVolatility(firm, dateStart, dateEnd, crsp)))
firm = "TSLA"
dateStart = "20100630"
dateEnd = "20181231"
print("Expected: -1 Actual: " + str(u.abnormalVolatility(firm, dateStart, dateEnd, crsp)))
"""

"""
Test: illiquidityMeasureDate functionality
firm = "ORCL"
date = "20000103"
print("Expected: -6.12906543405 Actual: " + str(u.illiquidityMeasureDate(firm, date, crsp)))
firm = "TSLA"
date = "20181231"
print("Expected: -7.58396387087 Actual: " + str(u.illiquidityMeasureDate(firm, date, crsp)))
firm = "FAKE"
date = "20181231"
print("Expected: -1 Actual: " + str(u.illiquidityMeasureDate(firm, date, crsp)))
"""

"""
Test: illiquidity functionality
firm = "ORCL"
dateStart = "20000103"
dateEnd = "20000107"
start = time.time()
print("Expected: -6.09853739932 Actual: " + str(u.illiquidity(firm, dateStart, dateEnd, crsp)))
end = time.time()
print("Time elapsed: " + str(end - start))
firm = "TSLA"
dateStart = "20181221"
dateEnd = "20181228"
print("Expected: -5.16466274207 Actual: " + str(u.illiquidity(firm, dateStart, dateEnd, crsp)))
firm = "ORCL"
dateStart = "20000102"
dateEnd = "20000103"
print("Expected: -1 Actual: " + str(u.illiquidity(firm, dateStart, dateEnd, crsp)))
"""

"""
Test: bookValue functionality
firm = "ORCL"
date = "20000531"
print("Expected: 3984288000.0 Actual: " + str(u.bookValue(firm, date, compustat)))
firm = "AAL"
date = "20181231"
print("Expected: -568000000.0 Actual: " + str(u.bookValue(firm, date, compustat)))
firm = "FAKE"
date = "20181231"
print("Expected: -1 Actual: " + str(u.bookValue(firm, date, compustat)))
"""

"""
Test: bookToMarketCap functionality
firm = "ORCL"
date = "20000531"
print("Expected: 0.01937368311 Actual: " + str(u.bookToMarketCap(firm, date, crsp, compustat)))
firm = "ORCL"
date = "20000103"
print("Expected: -1 Actual: " + str(u.bookToMarketCap(firm, date, crsp, compustat)))
firm = "TSLA"
date = "20181231"
print("Expected: 0.07772559827 Actual: " + str(u.bookToMarketCap(firm, date, crsp, compustat)))
"""

"""
Test: generateXList functionality
# first computation will always be slow
firm = "AAPL"
date = "20150721"
start = time.time()
print("Output: " + str(u.generateXList(firm, date, db, crsp, compustat)))
end = time.time()
print("Time elapsed first: " + str(end - start))
# all subsequent computations on the same day are extremely fast
firm = "MSFT"
date = "20150721"
start = time.time()
print("Output: " + str(u.generateXList(firm, date, db, crsp, compustat)))
end = time.time()
print("Time elapsed same: " + str(end - start))
# first computation on the next business day is somewhat slow
firm = "QCOM"
date = "20150722"
start = time.time()
print("Output: " + str(u.generateXList(firm, date, db, crsp, compustat)))
end = time.time()
print("Time elapsed next: " + str(end - start))
# all subsequent computations on the same day are extremely fast
firm = "BA"
date = "20150722"
print("Output: " + str(u.generateXList(firm, date, db, crsp, compustat)))
"""


