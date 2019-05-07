# extract_news.py
# -------
# Extracts news measures and writes a new CSV
import databases as d
import utils as u

mdb = d.AdjustableMeasuresDatabase("reduced_djn_data.csv")
new_name = "news_measures.csv"

# Create file and write header
f = open(new_name, "w+")
header = "DATE,TICKER,STORIES,TERMS,ABN_PCT_OLD,ABN_PCT_REC\n"
f.write(header)

for tup in mdb.tdMap:
    line = tup[1] + "," + tup[0]
    line += "," + str(u.stories(tup[0], tup[1], mdb))
    line += "," + str(u.terms(tup[0], tup[1], mdb))
    line += "," + str(u.abnormalPercentageOld(tup[0], tup[1], mdb))
    line += "," + str(u.abnormalPercentageRecombinations(tup[0], tup[1], mdb))
    line += "\n"
    f.write(line)







