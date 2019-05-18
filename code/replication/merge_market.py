# merge_market.py
# -------
# Merges COMPUSTAT and CRSP and writes a new CSV
import databases as d
import utils as u

compustat = d.PandasDatabase("reduced_compustat_full.csv")
crsp = d.CRSPDatabase("reduced_crsp_full.csv")

# CSVs should already share the same tickers after clean.py
crsp.recordTickers("TICKER", False)
crsp.recordDates("date", False)
dates = list(map(str, crsp.dates))

# Create file and write header
new_name = "market_measures.csv"
f = open(new_name, "w+")
header = "DATE,TICKER,RETX,BM,MCAP,LN_MCAP,VOLUME_FRAC,ILLIQ\n"
f.write(header)

for date in dates:
    for tic in crsp.tics:
        # ensure valid entries for each row
        entries = []
        retx = u.firmReturn(tic, date, crsp, False)
        if retx == -1:
            continue
        entries.append(str(retx))
        bm = u.bookToMarketCap(tic, date, crsp, compustat, False)
        if bm == -1:
            continue
        entries.append(str(bm))
        mcap = u.marketCap(tic, date, crsp, False)
        if mcap == -1:
            continue
        entries.append(str(mcap))
        ln_mcap = u.marketCapLN(tic, date, crsp, False)
        if ln_mcap == -1:
            continue
        entries.append(str(ln_mcap))
        volume_frac = u.firmVolumeFrac(tic, date, crsp, False)
        if volume_frac == -1:
            continue
        entries.append(str(volume_frac))
        illiq = u.illiquidityMeasureDate(tic, date, crsp, False)
        if illiq == -1:
            continue
        entries.append(str(illiq))
        # write the line
        line = date + "," + tic + "," + entries[0] + "," + entries[1] + "," + entries[2] + "," + entries[3] + "," +\
            entries[4] + "," + entries[5] + "\n"
        f.write(line)

f.close()

