# generate.py
# -------
# Writes out file with data to run for equations (8), (9), (10), (11), (12), (13) from Section 3
import generate_reg_data as gen
import databases as d

# setup databases to read in from
compustat = d.PandasDatabase("compustatQlarge.csv")
crsp = d.CRSPDatabase("crspdaystocklarge.csv")
mdb = d.AdjustableMeasuresDatabase("djn_data.csv")
# Find shared firms between databases
compustat.recordTickers("tic", False)
crsp.recordTickers("TICKER", False)
sharedTics = list(set(compustat.tics) & set(crsp.tics) & set(mdb.tics.keys()))
crsp.setAllowedTics(sharedTics)
# Use crsp dates as shared dates
crsp.recordDates("date", False)
sharedDates = list(map(str, crsp.dates))
print("SETUP DONE")

usingDates = ['20000103', '20000104']

# Equation (8)
gen.generate_csv8_9(usingDates, sharedTics, mdb, crsp, compustat)
"""
# Equation (9)
gen.generate_csv8_9(sharedDates, sharedTics, mdb, crsp, compustat, False)

# Equation (10)
gen.generate_csv10_11(sharedDates, sharedTics, mdb, crsp, compustat)

# Equation (11)
gen.generate_csv10_11(sharedDates, sharedTics, mdb, crsp, compustat, False)
"""

"""
# Equation (12)
t1 = -1
t2 = -1
gen.generate_csv12(sharedDates, sharedTics, mdb, crsp, compustat, t1, t2)
"""




