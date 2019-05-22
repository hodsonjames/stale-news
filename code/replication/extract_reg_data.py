# extract_reg_data.py
# -------
# Functions to write out file with data to run for equations (8), (9), (10), (11), (12), (13) from Section 3
import databases as d


def generate_csv8_9(news_file_name, market_file_name, eight=True):
    """
    Writes csv file for regression computation
    eight: True computes equation 8, False computes equation 9
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
    header = "date,dependent,AbnPctOld,Stories,AbnStories,Terms,MCap,BM,AbnRet,AbnVol,AbnVolatility,Illiq\n"
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
            # split line: 0:DATE,1:TICKER,2:LN_MCAP,3:ILLIQ,4:BM,5:ABN_RET,6:ABN_VOLUME,7:ABN_VOLATILITY
            current_market = line.rstrip('\n').split(',')
            # split line: 0:DATE,1:TICKER,2:STORIES,3:TERMS,4:ABN_PCT_OLD,5:ABN_PCT_REC
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
            # edge case, updated news date passes current market date
            if current_market[0] < current_news[0]:
                continue
            # check ticker alignment
            if current_market[1] < current_news[1]:
                continue
            while current_news[1] < current_market[1]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
            if terminate:
                break
            # edge case, updated news ticker passes current market ticker
            if current_market[1] < current_news[1]:
                continue
            # Create line with date (t)
            out_line = current_market[0]
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
            out_line += "\n"
            g.write(out_line)
    news_f.close()
    g.close()


def generate_csv10_11(news_file_name, market_file_name, ten=True):
    """
    Writes csv file for regression computation
    ten: True computes equation 10, False computes equation 11
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
             "Terms,MCap,BM,AbnRet,AbnVol,AbnVolatility,Illiq\n"
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
            # split line: 0:DATE,1:TICKER,2:LN_MCAP,3:ILLIQ,4:BM,5:ABN_RET,6:ABN_VOLUME,7:ABN_VOLATILITY
            current_market = line.rstrip('\n').split(',')
            # split line: 0:DATE,1:TICKER,2:STORIES,3:TERMS,4:ABN_PCT_OLD,5:ABN_PCT_REC
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
            # edge case, updated news date passes current market date
            if current_market[0] < current_news[0]:
                continue
            # check ticker alignment
            if current_market[1] < current_news[1]:
                continue
            while current_news[1] < current_market[1]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
            if terminate:
                break
            # edge case, updated news ticker passes current market ticker
            if current_market[1] < current_news[1]:
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
            out_line += "\n"
            g.write(out_line)
    news_f.close()
    g.close()


def generate_csv12(news_file_name, market_file_name, t1, t2):
    """
    Writes csv file for regression computation using offsets t1 and t2
    """
    # Set up database of news_file
    news_db = d.ProcessedNewsDatabase(news_file_name)
    market_db = d.ProcessedMarketDatabase(market_file_name)
    # Create output file and write header
    file_name = "reg_data_eq_12_t1_" + str(t1) + "_t2_" + str(t2) + ".csv"
    g = open(file_name, "w+")
    header = "date,dependent,AbnPcrOld,AbnPcrOldXAbnRet,AbnRet,AbnPcrRecombination,AbnPcrRecombinationXAbnRet" \
             ",Stories,AbnStories,Terms,MCap,BM,AbnRetVect,AbnVol,AbnVolatility,Illiq\n"
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
            # split line: 0:DATE,1:TICKER,2:LN_MCAP,3:ILLIQ,4:BM,5:ABN_RET,6:ABN_VOLUME,7:ABN_VOLATILITY
            current_market = line.rstrip('\n').split(',')
            # split line: 0:DATE,1:TICKER,2:STORIES,3:TERMS,4:ABN_PCT_OLD,5:ABN_PCT_REC
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
            # edge case, updated news date passes current market date
            if current_market[0] < current_news[0]:
                continue
            # check ticker alignment
            if current_market[1] < current_news[1]:
                continue
            while current_news[1] < current_market[1]:
                news_index += 1
                if news_index >= len(news_lines):
                    terminate = True
                    break
                current_news = news_lines[news_index].rstrip('\n').split(',')
            if terminate:
                break
            # edge case, updated news ticker passes current market ticker
            if current_market[1] < current_news[1]:
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
            out_line += "\n"
            g.write(out_line)
    news_f.close()
    g.close()


"""
generate_csv8_9("news_measures.csv", "market_measures.csv")
generate_csv8_9("news_measures.csv", "market_measures.csv", False)
generate_csv10_11("news_measures.csv", "market_measures.csv")
generate_csv10_11("news_measures.csv", "market_measures.csv", False)
generate_csv12("news_measures.csv", "market_measures.csv", 2, 4)
generate_csv12("news_measures.csv", "market_measures.csv", 2, 6)
generate_csv12("news_measures.csv", "market_measures.csv", 2, 11)
"""
