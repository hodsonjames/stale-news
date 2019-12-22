# extract_reg_data.py
# -------
# Functions to write out file with data to run for equations (8), (9), (10), (11), (12), (13) from Section 3
import databases as d
import utils_direct as ud


def generate_csv8_9(news_file_name, market_file_name, eight=True, earnings=False, weekday=False, industry=False,
                    firm_size=False, include_ticker=False):
    """
    Writes csv file for regression computation
    eight: True computes equation 8, False computes equation 9
    earnings: True adds earnings control column
    weekday: Adds 4 dummies for date is a Tuesday, Wednesday, Thursday, Friday (with Monday excluded)
    industry: Adds 19 dummies for firm industries type (with 11 Agriculture excluded)
    firm_size: Adds 4 dummies for firm size in ex ante lineup (with 1st quintile excluded)
    """
    # Set up database of news_file
    news_db = d.ProcessedNewsDatabase(news_file_name)
    market_db = d.ProcessedMarketDatabase(market_file_name)
    # Create output file and write header
    if eight:
        file_name = "reg_data_eq_8.csv"
    else:
        file_name = "reg_data_eq_9.csv"
    g = open(file_name, "w+")
    header = "date,dependent,AbnPctOld,Stories,AbnStories,Terms,MCap,BM,AbnRet,AbnVol,AbnVolatility,Illiq"
    if include_ticker:
        header = "TICKER," + header
    if earnings:
        header += ",Earnings"
    if weekday:
        header += ",Tuesday,Wednesday,Thursday,Friday"
    if industry:
        header += ",Extraction,Utilities,Construction,Manufacturing,Wholesale,Retail,Transportation," \
                  "Information,Finance,Estate,Professional,Management,Administrative,Educational," \
                  "Health,Entertainment,Accommodation,Other,Public"
    if firm_size:
        header += ",Size2,Size3,Size4,Size5"
    header += "\n"
    g.write(header)

    dates = list(market_db.dates.keys())
    news_f = open(news_file_name)
    news_f.readline()  # skip header
    news_lines = news_f.readlines()
    news_index = 0
    terminate = False
    with open(market_file_name) as market_f:
        skip = True
        for line in market_f:
            if skip:
                skip = False
                continue
            # split line: 0:DATE,1:TICKER,2:LN_MCAP,3:ILLIQ,4:BM,5:ABN_RET,6:ABN_VOLUME,7:ABN_VOLATILITY,8:REPORT,
            # 9:INDUSTRY,10:FIRM_SIZE
            current_market = line.rstrip('\n').split(',')
            # split line: 0:DATE,1:TICKER,2:STORIES,3:TERMS,4:ABN_PCT_OLD,5:ABN_PCT_REC,6:RECOMB_STORIES
            current_news = news_lines[news_index].rstrip('\n').split(',')
            # check date alignment
            if current_market[0] < current_news[0]:
                continue
            while current_news[0] < current_market[0]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
            if terminate:
                break
            # updated news ticker passes current market ticker or updated news date passes current market date
            if current_market[0] < current_news[0] or current_market[1] < current_news[1]:
                continue
            while current_news[1] < current_market[1]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
                # make sure date still aligned
                if current_market[0] < current_news[0]:
                    break
            if terminate:
                break
            # updated news ticker passes current market ticker or updated news date passes current market date
            if current_market[0] < current_news[0] or current_market[1] < current_news[1]:
                continue
            # Create line with date (t)
            out_line = current_market[0]
            if include_ticker:
                out_line = current_market[1] + "," + out_line
            # append dependent (t+1)
            t_plus_1 = dates.index(current_market[0]) + 1
            if t_plus_1 >= len(dates):
                continue
            if eight:
                if dates[t_plus_1] not in market_db.abn_ret[current_market[1]]:
                    continue
                out_line += "," + str(abs(market_db.abn_ret[current_market[1]][dates[t_plus_1]]))
            else:
                if dates[t_plus_1] not in market_db.abn_vol[current_market[1]]:
                    continue
                out_line += "," + str(market_db.abn_vol[current_market[1]][dates[t_plus_1]])
            # append AbnPctOld (t)
            out_line += "," + current_news[4]
            # append Stories (t)
            out_line += "," + current_news[2]
            # append AbnStories ([t-5, t-1])
            temp = news_db.abnormalStories(current_news[1], current_news[0])
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append Terms (t)
            out_line += "," + current_news[3]
            # append MCap (t)
            out_line += "," + current_market[2]
            # append BM (t)
            out_line += "," + current_market[4]
            # append AbnRet ([t-5, t-1])
            temp = market_db.abnormalReturn(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append AbnVol ([t-5, t-1])
            temp = market_db.abnormalVol(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append AbnVolatility ([t-5, t-1])
            temp = market_db.abnormalVolatility(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append Illiq ([t-5, t-1])
            temp = market_db.illiquidity(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            if earnings:
                # append Earnings (t)
                if eval(current_market[8]):
                    out_line += "," + str(1)
                else:
                    out_line += "," + str(0)
            if weekday:
                # append day of week dummies for day (t)
                day_number = ud.day_of_week(current_market[0])
                for i in range(1, 5):
                    if i == day_number:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            if industry:
                # append industry dummies for firm (i)
                permitted_codes = ["21", "22", "23", "31", "42", "44", "48", "51", "52", "53", "54", "55", "56", "61",
                                   "62", "71", "72", "81", "92"]
                for code in permitted_codes:
                    if code == current_market[9]:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            if firm_size:
                # append firm size dummies for firm (i)
                for i in range(2, 6):
                    if str(i) == current_market[10]:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            out_line += "\n"
            g.write(out_line)
    news_f.close()
    g.close()


def generate_csv10_11(news_file_name, market_file_name, ten=True, earnings=False, weekday=False, industry=False,
                      firm_size=False):
    """
    Writes csv file for regression computation
    ten: True computes equation 10, False computes equation 11
    earnings: True adds earnings control column
    weekday: Adds 4 dummies for date is a Tuesday, Wednesday, Thursday, Friday (with Monday excluded)
    industry: Adds 19 dummies for firm industries type (with 11 Agriculture excluded)
    firm_size: Adds 4 dummies for firm size in ex ante lineup (with 1st quintile excluded)
    """
    # Set up database of news_file
    news_db = d.ProcessedNewsDatabase(news_file_name)
    market_db = d.ProcessedMarketDatabase(market_file_name)
    # Create output file and write header
    if ten:
        file_name = "reg_data_eq_10.csv"
    else:
        file_name = "reg_data_eq_11.csv"
    g = open(file_name, "w+")
    header = "date,dependent,AbnPctOld,AbnPcrRecombinations,Stories,AbnStories," \
             "Terms,MCap,BM,AbnRet,AbnVol,AbnVolatility,Illiq"
    if earnings:
        header += ",Earnings"
    if weekday:
        header += ",Tuesday,Wednesday,Thursday,Friday"
    if industry:
        header += ",Extraction,Utilities,Construction,Manufacturing,Wholesale,Retail,Transportation," \
                  "Information,Finance,Estate,Professional,Management,Administrative,Educational," \
                  "Health,Entertainment,Accommodation,Other,Public"
    if firm_size:
        header += ",Size2,Size3,Size4,Size5"
    header += "\n"
    g.write(header)

    dates = list(market_db.dates.keys())
    news_f = open(news_file_name)
    news_f.readline()  # skip header
    news_lines = news_f.readlines()
    news_index = 0
    terminate = False
    with open(market_file_name) as market_f:
        skip = True
        for line in market_f:
            if skip:
                skip = False
                continue
            # split line: 0:DATE,1:TICKER,2:LN_MCAP,3:ILLIQ,4:BM,5:ABN_RET,6:ABN_VOLUME,7:ABN_VOLATILITY,8:REPORT,
            # 9:INDUSTRY,10:FIRM_SIZE
            current_market = line.rstrip('\n').split(',')
            # split line: 0:DATE,1:TICKER,2:STORIES,3:TERMS,4:ABN_PCT_OLD,5:ABN_PCT_REC,6:RECOMB_STORIES
            current_news = news_lines[news_index].rstrip('\n').split(',')
            # check date alignment
            if current_market[0] < current_news[0]:
                continue
            while current_news[0] < current_market[0]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
            if terminate:
                break
            # updated news ticker passes current market ticker or updated news date passes current market date
            if current_market[0] < current_news[0] or current_market[1] < current_news[1]:
                continue
            while current_news[1] < current_market[1]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
                # make sure date still aligned
                if current_market[0] < current_news[0]:
                    break
            if terminate:
                break
            # updated news ticker passes current market ticker or updated news date passes current market date
            if current_market[0] < current_news[0] or current_market[1] < current_news[1]:
                continue
            # Create line with date (t)
            out_line = current_market[0]
            # append dependent (t+1)
            t_plus_1 = dates.index(current_market[0]) + 1
            if t_plus_1 >= len(dates):
                continue
            if ten:
                if dates[t_plus_1] not in market_db.abn_ret[current_market[1]]:
                    continue
                out_line += "," + str(abs(market_db.abn_ret[current_market[1]][dates[t_plus_1]]))
            else:
                if dates[t_plus_1] not in market_db.abn_vol[current_market[1]]:
                    continue
                out_line += "," + str(market_db.abn_vol[current_market[1]][dates[t_plus_1]])
            # append AbnPctOld (t)
            out_line += "," + current_news[4]
            # append AbnPcrRecombinations (t)
            out_line += "," + current_news[5]
            # append Stories (t)
            out_line += "," + current_news[2]
            # append AbnStories ([t-5, t-1])
            temp = news_db.abnormalStories(current_news[1], current_news[0])
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append Terms (t)
            out_line += "," + current_news[3]
            # append MCap (t)
            out_line += "," + current_market[2]
            # append BM (t)
            out_line += "," + current_market[4]
            # append AbnRet ([t-5, t-1])
            temp = market_db.abnormalReturn(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append AbnVol ([t-5, t-1])
            temp = market_db.abnormalVol(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append AbnVolatility ([t-5, t-1])
            temp = market_db.abnormalVolatility(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append Illiq ([t-5, t-1])
            temp = market_db.illiquidity(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            if earnings:
                # append Earnings (t)
                if eval(current_market[8]):
                    out_line += "," + str(1)
                else:
                    out_line += "," + str(0)
            if weekday:
                # append day of week dummies for day (t)
                day_number = ud.day_of_week(current_market[0])
                for i in range(1, 5):
                    if i == day_number:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            if industry:
                # append industry dummies for firm (i)
                permitted_codes = ["21", "22", "23", "31", "42", "44", "48", "51", "52", "53", "54", "55", "56", "61",
                                   "62", "71", "72", "81", "92"]
                for code in permitted_codes:
                    if code == current_market[9]:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            if firm_size:
                # append firm size dummies for firm (i)
                for i in range(2, 6):
                    if str(i) == current_market[10]:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            out_line += "\n"
            g.write(out_line)
    news_f.close()
    g.close()


def generate_csv12(news_file_name, market_file_name, t1, t2, earnings=False, weekday=False, industry=False,
                   firm_size=False):
    """
    Writes csv file for regression computation using offsets t1 and t2
    earnings: True adds earnings control column
    weekday: Adds 4 dummies for date is a Tuesday, Wednesday, Thursday, Friday (with Monday excluded)
    industry: Adds 19 dummies for firm industries type (with 11 Agriculture excluded)
    firm_size: Adds 4 dummies for firm size in ex ante lineup (with 1st quintile excluded)
    """
    # Set up database of news_file
    news_db = d.ProcessedNewsDatabase(news_file_name)
    market_db = d.ProcessedMarketDatabase(market_file_name)
    # Create output file and write header
    file_name = "reg_data_eq_12_t1_" + str(t1) + "_t2_" + str(t2) + ".csv"
    g = open(file_name, "w+")
    header = "date,dependent,AbnPcrOld,AbnPcrOldXAbnRet,AbnRet,AbnPcrRecombination,AbnPcrRecombinationXAbnRet" \
             ",Stories,AbnStories,Terms,MCap,BM,AbnRetVect,AbnVol,AbnVolatility,Illiq"
    if earnings:
        header += ",Earnings"
    if weekday:
        header += ",Tuesday,Wednesday,Thursday,Friday"
    if industry:
        header += ",Extraction,Utilities,Construction,Manufacturing,Wholesale,Retail,Transportation," \
                  "Information,Finance,Estate,Professional,Management,Administrative,Educational," \
                  "Health,Entertainment,Accommodation,Other,Public"
    if firm_size:
        header += ",Size2,Size3,Size4,Size5"
    header += "\n"
    g.write(header)

    dates = list(market_db.dates.keys())
    news_f = open(news_file_name)
    news_f.readline()  # skip header
    news_lines = news_f.readlines()
    news_index = 0
    terminate = False
    with open(market_file_name) as market_f:
        skip = True
        for line in market_f:
            if skip:
                skip = False
                continue
            # split line: 0:DATE,1:TICKER,2:LN_MCAP,3:ILLIQ,4:BM,5:ABN_RET,6:ABN_VOLUME,7:ABN_VOLATILITY,8:REPORT,
            # 9:INDUSTRY,10:FIRM_SIZE
            current_market = line.rstrip('\n').split(',')
            # split line: 0:DATE,1:TICKER,2:STORIES,3:TERMS,4:ABN_PCT_OLD,5:ABN_PCT_REC,6:RECOMB_STORIES
            current_news = news_lines[news_index].rstrip('\n').split(',')
            # check date alignment
            if current_market[0] < current_news[0]:
                continue
            while current_news[0] < current_market[0]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
            if terminate:
                break
            # updated news ticker passes current market ticker or updated news date passes current market date
            if current_market[0] < current_news[0] or current_market[1] < current_news[1]:
                continue
            while current_news[1] < current_market[1]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
                # make sure date still aligned
                if current_market[0] < current_news[0]:
                    break
            if terminate:
                break
            # updated news ticker passes current market ticker or updated news date passes current market date
            if current_market[0] < current_news[0] or current_market[1] < current_news[1]:
                continue
            # Create line with date (t)
            out_line = current_market[0]
            # append dependent ([t+t1, t+t2])
            temp = market_db.abnormalReturn(current_market[1], current_market[0], t1, t2)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append AbnPcrOld (t)
            out_line += "," + current_news[4]
            # append AbnPcrOld (t) X AbnRet (t+1)
            t_plus_1 = dates.index(current_market[0]) + 1
            if t_plus_1 >= len(dates):
                continue
            if dates[t_plus_1] not in market_db.abn_ret[current_market[1]]:
                continue
            abn_ret_1 = market_db.abn_ret[current_market[1]][dates[t_plus_1]]
            out_line += "," + str(float(current_news[4]) * abn_ret_1)
            # append AbnRet (t+1)
            out_line += "," + str(abn_ret_1)
            # append AbnPcrRecombination (t)
            out_line += "," + current_news[5]
            # append AbnPcrRecombination (t) X AbnRet (t+1)
            out_line += "," + str(float(current_news[5]) * abn_ret_1)
            # append Stories (t)
            out_line += "," + current_news[2]
            # append AbnStories ([t-5, t-1])
            temp = news_db.abnormalStories(current_news[1], current_news[0])
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append Terms (t)
            out_line += "," + current_news[3]
            # append MCap (t)
            out_line += "," + current_market[2]
            # append BM (t)
            out_line += "," + current_market[4]
            # append AbnRetVect ([t-5, t-1])
            temp = market_db.abnormalReturn(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append AbnVol ([t-5, t-1])
            temp = market_db.abnormalVol(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append AbnVolatility ([t-5, t-1])
            temp = market_db.abnormalVolatility(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            # append Illiq ([t-5, t-1])
            temp = market_db.illiquidity(current_market[1], current_market[0], -5, -1)
            if temp == -1:
                continue
            out_line += "," + str(temp)
            if earnings:
                # append Earnings (t)
                if eval(current_market[8]):
                    out_line += "," + str(1)
                else:
                    out_line += "," + str(0)
            if weekday:
                # append day of week dummies for day (t)
                day_number = ud.day_of_week(current_market[0])
                for i in range(1, 5):
                    if i == day_number:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            if industry:
                # append industry dummies for firm (i)
                permitted_codes = ["21", "22", "23", "31", "42", "44", "48", "51", "52", "53", "54", "55", "56", "61",
                                   "62", "71", "72", "81", "92"]
                for code in permitted_codes:
                    if code == current_market[9]:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            if firm_size:
                # append firm size dummies for firm (i)
                for i in range(2, 6):
                    if str(i) == current_market[10]:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            out_line += "\n"
            g.write(out_line)
    news_f.close()
    g.close()


def generate_csv13(eq_10_file_name):
    """
    Writes csv file for yearly regression computation
    """
    # Create first year output file
    file_year = "2001"
    file_root = "reg_data_eq_13_"
    file_name = file_root + file_year + ".csv"
    header = ""

    g = open(file_name, "w+")

    with open(eq_10_file_name) as f:
        skip = True
        for line in f:
            if skip:
                skip = False
                header = line
                g.write(header)
                continue
            # split line: 0:date ...
            current = line.rstrip('\n').split(',')
            current_year = current[0][:4]
            if current_year != file_year:
                # prepare next file
                g.close()
                file_year = current_year
                file_name = file_root + file_year + ".csv"
                g = open(file_name, "w+")
                g.write(header)
            else:
                g.write(line)
        # tail case
        g.close()


def generate_csv_recomb_on_size(news_file_name, market_file_name, relative=True, earnings=False, weekday=False,
                                industry=False):
    """
    Writes csv file for regression computation of recombination stories of firm on log firm market cap
    relative: True uses percentage recombination stories as dependent, False uses count recombination stories
    earnings: True adds earnings control column
    weekday: Adds 4 dummies for date is a Tuesday, Wednesday, Thursday, Friday (with Monday excluded)
    industry: Adds 19 dummies for firm industries type (with 11 Agriculture excluded)
    """
    # Create output file and write header
    if relative:
        file_name = "reg_data_recomb_on_size_relative.csv"
    else:
        file_name = "reg_data_recomb_on_size_count.csv"
    g = open(file_name, "w+")
    header = "date,dependent,MCap"
    if earnings:
        header += ",Earnings"
    if weekday:
        header += ",Tuesday,Wednesday,Thursday,Friday"
    if industry:
        header += ",Extraction,Utilities,Construction,Manufacturing,Wholesale,Retail,Transportation," \
                  "Information,Finance,Estate,Professional,Management,Administrative,Educational," \
                  "Health,Entertainment,Accommodation,Other,Public"
    header += "\n"
    g.write(header)

    news_f = open(news_file_name)
    news_f.readline()  # skip header
    news_lines = news_f.readlines()
    news_index = 0
    terminate = False
    with open(market_file_name) as market_f:
        skip = True
        for line in market_f:
            if skip:
                skip = False
                continue
            # split line: 0:DATE,1:TICKER,2:LN_MCAP,3:ILLIQ,4:BM,5:ABN_RET,6:ABN_VOLUME,7:ABN_VOLATILITY,8:REPORT,
            # 9:INDUSTRY,10:FIRM_SIZE
            current_market = line.rstrip('\n').split(',')
            # split line: 0:DATE,1:TICKER,2:STORIES,3:TERMS,4:ABN_PCT_OLD,5:ABN_PCT_REC,6:RECOMB_STORIES
            current_news = news_lines[news_index].rstrip('\n').split(',')
            # check date alignment
            if current_market[0] < current_news[0]:
                continue
            while current_news[0] < current_market[0]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
            if terminate:
                break
            # updated news ticker passes current market ticker or updated news date passes current market date
            if current_market[0] < current_news[0] or current_market[1] < current_news[1]:
                continue
            while current_news[1] < current_market[1]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
                # make sure date still aligned
                if current_market[0] < current_news[0]:
                    break
            if terminate:
                break
            # updated news ticker passes current market ticker or updated news date passes current market date
            if current_market[0] < current_news[0] or current_market[1] < current_news[1]:
                continue
            # Create line with date (t)
            out_line = current_market[0]
            # append dependent (t)
            if relative:
                out_line += "," + str(int(current_news[6]) / int(current_news[2]))
            else:
                out_line += "," + current_news[6]
            # append MCap (t)
            out_line += "," + current_market[2]
            if earnings:
                # append Earnings (t)
                if eval(current_market[8]):
                    out_line += "," + str(1)
                else:
                    out_line += "," + str(0)
            if weekday:
                # append day of week dummies for day (t)
                day_number = ud.day_of_week(current_market[0])
                for i in range(1, 5):
                    if i == day_number:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            if industry:
                # append industry dummies for firm (i)
                permitted_codes = ["21", "22", "23", "31", "42", "44", "48", "51", "52", "53", "54", "55", "56", "61",
                                   "62", "71", "72", "81", "92"]
                for code in permitted_codes:
                    if code == current_market[9]:
                        out_line += "," + str(1)
                    else:
                        out_line += "," + str(0)
            out_line += "\n"
            g.write(out_line)
    news_f.close()
    g.close()


# Regression data with earnings control
generate_csv8_9("news_measures.csv", "market_measures.csv", True, True, True, True, True)
generate_csv8_9("news_measures.csv", "market_measures.csv", False, True, True, True, True,)
generate_csv10_11("news_measures.csv", "market_measures.csv", True, True, True, True, True)
generate_csv10_11("news_measures.csv", "market_measures.csv", False, True, True, True, True)
# Regressions for reversal with controls
generate_csv12("news_measures.csv", "market_measures.csv", 2, 4, True, True, True, True)
generate_csv12("news_measures.csv", "market_measures.csv", 2, 6, True, True, True, True)
generate_csv12("news_measures.csv", "market_measures.csv", 2, 11, True, True, True, True)
# Regression for time series
generate_csv13("reg_data_eq_10.csv")
# Regressions for recombinations on firm size with controls
generate_csv_recomb_on_size("news_measures.csv", "market_measures.csv", True, True, True, True)
generate_csv_recomb_on_size("news_measures.csv", "market_measures.csv", False, True, True, True)
