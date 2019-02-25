import databases as d
import utils as u

db = d.MeasuresDatabase("simulated_data.txt")

"""
Test: MeasuresDatabase tickerMap functionality
count = 0
for k in db.tickerMap:
    print("TICKER: " + k)
    for row in db.tickerMap.get(k):
        print(row)
        count += 1
print(count)
"""

"""
Test: MeasuresDatabase dateMap functionality
count = 0
for k in db.dateMap:
    print("DATE: " + k)
    for row in db.dateMap.get(k):
        print(row)
        count += 1
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
print("Expected: -1 Actual: " + str(u.stories("DOES NOT EXIST", "20150611", db)))
print("Expected: 0 Actual: " + str(u.stories("TWTR", "302123231", db)))
"""

"""
Test: terms functionality
print("Expected: 208.5 Actual: " + str(u.terms("PRGO", "20150421", db)))
print("Expected: 97.0 Actual: " + str(u.terms("TWTR", "20150611", db)))
print("Expected: -1 Actual: " + str(u.terms("DOES NOT EXIST", "20150611", db)))
print("Expected: 0 Actual: " + str(u.terms("TWTR", "302123231", db)))
"""

"""
Test: abnormalStories functionality
print("Expected: -1 Actual: " + str(u.abnormalStories("PRGO", "20150421", db)))
print("Expected: 0.32727272727272727 Actual: " + str(u.abnormalStories("FCAU", "20150730", db)))
print("Expected: -0.07272727272727272 Actual: " + str(u.abnormalStories("AAPL", "20150721", db)))
"""
