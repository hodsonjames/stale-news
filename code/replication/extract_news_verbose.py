# extract_news_verbose.py
# -------
# Extracts news measures and writes a new CSV, sorted first by date and then by ticker
import databases as d
import utils as u
import pandas as pd

mdb = d.AdjustableMeasuresDatabase("reduced_djn_data.csv")
new_name = "news_measures_verbose.csv"

# Create file and write header
f = open(new_name, "w+")
header = "DATE,TICKER,STORIES,TERMS,ABN_PCT_OLD,ABN_PCT_REC,RECOMB_STORIES,PCT_OLD,PCT_REC\n"
f.write(header)

# Will maintain date order
for tup in mdb.tdMap:
    line = tup[1] + "," + tup[0]
    line += "," + str(u.stories(tup[0], tup[1], mdb))
    line += "," + str(u.terms(tup[0], tup[1], mdb))
    line += "," + str(u.abnormalPercentageOld(tup[0], tup[1], mdb))
    line += "," + str(u.abnormalPercentageRecombinations(tup[0], tup[1], mdb))
    line += "," + str(mdb.recstor[tup])
    line += "," + str(u.percentageOld(tup[0], tup[1], mdb))
    line += "," + str(u.percentageRecombinations(tup[0], tup[1], mdb))
    line += "\n"
    f.write(line)

f.close()

# Sort by date and ticker
df = pd.read_csv(new_name)
df.sort_values(by=["DATE", "TICKER"], inplace=True)
df.to_csv(new_name, index=False)





