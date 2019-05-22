# merge_market.py
# -------
# Merges COMPUSTAT and CRSP and writes a new CSV
import os
import databases as d
import utils_direct as ud
from collections import OrderedDict
import pandas as pd
import numpy as np

compustat = d.BookDatabase("reduced_compustat_full.csv")

# 1ST PASS
# Create intermediate file and write header
intermed_name_1 = "delete_temp_1.csv"
g = open(intermed_name_1, "w+")
header = "DATE,TICKER,RETX,MCAP,LN_MCAP,VOLUME_FRAC,ILLIQ,BM\n"
g.write(header)

# Used in 2ND PASS
date_to_total_mcap = OrderedDict()

with open("reduced_crsp_full.csv") as f:
    skip = True
    current_date = -1
    total_mcap = 0
    for line in f:
        if skip:
            skip = False
            continue
        # split line of crsp: 0:PERMNO,1:date,2:TICKER,3:PRC,4:VOL,5:SHROUT,6:OPENPRC,7:RETX,8:vwretx
        current = line.rstrip('\n').split(',')
        # skip if RETX is invalid
        if current[7] == 'C':
            continue
        # if this is a new day total market cap for the previous day is ready to store
        if current[1] != current_date:
            if current_date == -1:
                # initialize very first day
                current_date = current[1]
            else:
                date_to_total_mcap[current_date] = total_mcap
                current_date = current[1]
                total_mcap = 0
        # insert DATE, TICKER, RETX
        new_line = current[1] + "," + current[2] + "," + current[7]
        mcap = ud.marketCap(float(current[3]), float(current[5]))
        total_mcap += mcap
        # insert MCAP
        new_line += "," + str(mcap)
        # insert LN_MCAP
        new_line += "," + str(ud.marketCapLN(mcap))
        # insert VOLUME_FRAC
        new_line += "," + str(ud.firmVolumeFrac(float(current[4]), float(current[5])))
        # insert ILLIQ
        new_line += "," + str(ud.illiquidityMeasureDate(float(current[7]), float(current[4])))
        # insert BM
        book = compustat.getBookValue(current[2], current[1])
        if book == -1:
            new_line += "," + "-inf"
        else:
            new_line += "," + str(book / mcap)
        new_line += "\n"
        g.write(new_line)
    # last day total market cap still needs to be entered
    date_to_total_mcap[current_date] = total_mcap
g.close()

# Sort by date and ticker
df = pd.read_csv(intermed_name_1)
df.sort_values(by=["DATE", "TICKER"], inplace=True)
df.to_csv(intermed_name_1, index=False)

# 2ND Pass
# Create intermediate file and write header
intermed_name_2 = "delete_temp_2.csv"
g = open(intermed_name_2, "w+")
header = "DATE,TICKER,RETX,MCAP,LN_MCAP,VOLUME_FRAC,ILLIQ,BM,MC_WEIGHT\n"
g.write(header)

# Used in 3RD PASS
date_to_total_wret = OrderedDict()
date_to_total_wvol = OrderedDict()

with open(intermed_name_1) as f:
    skip = True
    current_date = -1
    total_wret = 0
    total_wvol = 0
    for line in f:
        if skip:
            skip = False
            continue
        # split line of: 0:DATE,1:TICKER,2:RETX,3:MCAP,4:LN_MCAP,5:VOLUME_FRAC,6:ILLIQ,7:BM
        current = line.rstrip('\n').split(',')
        # if this is a new day total weighted return and total weighted volume for the previous day are ready to store
        if current[0] != current_date:
            if current_date == -1:
                # initialize very first day
                current_date = current[0]
            else:
                date_to_total_wret[current_date] = total_wret
                date_to_total_wvol[current_date] = total_wvol
                current_date = current[0]
                total_wret = 0
                total_wvol = 0
        # append MC_WEIGHT
        mc_weight = float(current[3]) / date_to_total_mcap[current[0]]
        line = line.rstrip('\n')
        line += "," + str(mc_weight) + "\n"
        g.write(line)
        total_wret += float(current[2]) * mc_weight
        total_wvol += float(current[5]) * mc_weight
    # last day totals need to be entered
    date_to_total_wret[current_date] = total_wret
    date_to_total_wvol[current_date] = total_wvol
g.close()

# 3RD Pass
# Create file and write header
intermed_name_3 = "delete_temp_3.csv"
g = open(intermed_name_3, "w+")
header = "DATE,TICKER,RETX,MCAP,LN_MCAP,VOLUME_FRAC,ILLIQ,BM,MC_WEIGHT,ABN_RET,ABN_VOLUME\n"
g.write(header)

# Maps each ticker to a dictionary of dates to abnormal returns
ticker_to_date_to_abn_ret = {}
dates = OrderedDict()

with open(intermed_name_2) as f:
    skip = True
    for line in f:
        if skip:
            skip = False
            continue
        # split line of: 0:DATE,1:TICKER,2:RETX,3:MCAP,4:LN_MCAP,5:VOLUME_FRAC,6:ILLIQ,7:BM,8:MC_WEIGHT
        current = line.rstrip('\n').split(',')
        if current[0] not in dates:
            dates[current[0]] = None
        # append ABN_RET
        abn_ret = ud.abnormalReturnDate(float(current[2]), date_to_total_wret[current[0]])
        if current[1] in ticker_to_date_to_abn_ret:
            ticker_to_date_to_abn_ret[current[1]][current[0]] = abn_ret
        else:
            ticker_to_date_to_abn_ret[current[1]] = OrderedDict()
            ticker_to_date_to_abn_ret[current[1]][current[0]] = abn_ret
        line = line.rstrip('\n')
        line += "," + str(abn_ret)
        # append ABN_VOLUME
        abn_vol = ud.abnormalVolDate(float(current[5]), date_to_total_wvol[current[0]])
        line += "," + str(abn_vol)
        line += "\n"
        g.write(line)
g.close()

# Assigns daily abnVolatility for all firms, defined as
# Population standard deviation of abnormal returns for 20 business days prior to and including date given
dates = list(OrderedDict(sorted(dates.items(), key=lambda t: t[0])).keys())
# Maps each ticker to a dictionary of dates to abnormal volatility
ticker_to_date_to_abn_volat = {}
for tic in ticker_to_date_to_abn_ret:
    prior_returns = []
    sub_dict = ticker_to_date_to_abn_ret[tic]
    all_dates_index = 0
    for dat in sub_dict:
        if dat > dates[all_dates_index]:
            # missing measurement(s) for firm, so dat is ahead
            prior_returns = []
            while dates[all_dates_index] < dat:
                all_dates_index += 1
        # dat matches
        prior_returns.append(sub_dict[dat])
        if len(prior_returns) > 20:
            prior_returns.pop(0)
        if len(prior_returns) == 20:
            if tic in ticker_to_date_to_abn_volat:
                ticker_to_date_to_abn_volat[tic][dat] = np.std(prior_returns)
            else:
                ticker_to_date_to_abn_volat[tic] = OrderedDict()
                ticker_to_date_to_abn_volat[tic][dat] = np.std(prior_returns)
        all_dates_index += 1

# 4TH Pass
# Create file and write header
file_name = "market_measures.csv"
g = open(file_name, "w+")
header = "DATE,TICKER,LN_MCAP,ILLIQ,BM,ABN_RET,ABN_VOLUME,ABN_VOLATILITY\n"
g.write(header)

with open(intermed_name_3) as f:
    skip = True
    for line in f:
        if skip:
            skip = False
            continue
        # split line of: 0:DATE,1:TICKER,2:RETX,3:MCAP,4:LN_MCAP,5:VOLUME_FRAC,
        # 6:ILLIQ,7:BM,8:MC_WEIGHT,9:ABN_RET,10:ABN_VOLUME
        current = line.rstrip('\n').split(',')
        # drop rows with "-inf"
        if current[7] == "-inf" or current[6] == "-inf":
            continue
        if current[1] in ticker_to_date_to_abn_volat and current[0] in ticker_to_date_to_abn_volat[current[1]]:
            new_line = current[0] + "," + current[1] + "," + current[4] + "," + current[6] + "," + current[7] + \
                "," + current[9] + "," + current[10] + "," + \
                str(ticker_to_date_to_abn_volat[current[1]][current[0]]) + "\n"
            g.write(new_line)
g.close()

# Delete intermediate files
os.remove(intermed_name_1)
os.remove(intermed_name_2)
os.remove(intermed_name_3)


