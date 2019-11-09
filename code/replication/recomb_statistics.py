# recomb_statistics.py
# -------
# Computes mean and standard deviations of the number of recombination stories every day
import utils_direct as ud
import datetime as dt
import numpy as np

# lists of recombination article counts on each unique day of the week (e.g. every Monday available)
mon_recomb_counts = []
tue_recomb_counts = []
wed_recomb_counts = []
thu_recomb_counts = []
fri_recomb_counts = []

# lists of recombination articles as a percentage of all stories on a each unique day of the week
mon_recomb_percents = []
tue_recomb_percents = []
wed_recomb_percents = []
thu_recomb_percents = []
fri_recomb_percents = []

weekend_article_count = 0
first_day = -1
last_day = -1

with open("reduced_djn_data.csv") as f:
    skip = True
    current_date = -1
    current_day_of_week = -1
    current_date_total_recombs = -1
    current_date_total_stories = -1
    for line in f:
        # skip header
        if skip:
            skip = False
            continue
        # split line of djin: 0:DATE_EST,1:STORY_ID,2:TICKER,3:STORY_LENGTH,4:CLOSEST_ID,5:SECOND_CLOSEST_ID,
        # 6:CLOSEST_SCORE,7:TOTAL_OVERLAP,8:IS_OLD,9:IS_REPRINT,10:IS_RECOMB
        current = line.rstrip('\n').split(',')
        # convert date
        epoch = float(current[0])
        date = str(dt.datetime.utcfromtimestamp(epoch).strftime("%Y%m%d"))
        try:
            ud.day_of_week(date)
        except RuntimeError as e:
            # day is a weekend
            weekend_article_count += 1
            continue
        if date != current_date:
            if current_date == -1:
                # initialize very first day
                current_date = date
                current_day_of_week = ud.day_of_week(current_date)
                current_date_total_recombs = 0
                current_date_total_stories = 0
                first_day = current_date
            else:
                # process previous totals
                if current_day_of_week == 0:
                    mon_recomb_counts.append(current_date_total_recombs)
                    mon_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
                elif current_day_of_week == 1:
                    tue_recomb_counts.append(current_date_total_recombs)
                    tue_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
                elif current_day_of_week == 2:
                    wed_recomb_counts.append(current_date_total_recombs)
                    wed_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
                elif current_day_of_week == 3:
                    thu_recomb_counts.append(current_date_total_recombs)
                    thu_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
                elif current_day_of_week == 4:
                    fri_recomb_counts.append(current_date_total_recombs)
                    fri_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
                current_date = date
                current_day_of_week = ud.day_of_week(current_date)
                current_date_total_recombs = 0
                current_date_total_stories = 0
        current_date_total_stories += 1
        if eval(current[10]):
            current_date_total_recombs += 1
    # last day totals still needs to processed
    if current_day_of_week == 0:
        mon_recomb_counts.append(current_date_total_recombs)
        mon_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
    elif current_day_of_week == 1:
        tue_recomb_counts.append(current_date_total_recombs)
        tue_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
    elif current_day_of_week == 2:
        wed_recomb_counts.append(current_date_total_recombs)
        wed_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
    elif current_day_of_week == 3:
        thu_recomb_counts.append(current_date_total_recombs)
        thu_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
    elif current_day_of_week == 4:
        fri_recomb_counts.append(current_date_total_recombs)
        fri_recomb_percents.append(current_date_total_recombs/current_date_total_stories)
    last_day = current_date

mean = np.mean(mon_recomb_counts)
sd = np.std(mon_recomb_counts)
print("Monday (Count) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")
mean = np.mean(tue_recomb_counts)
sd = np.std(tue_recomb_counts)
print("Tuesday (Count) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")
mean = np.mean(wed_recomb_counts)
sd = np.std(wed_recomb_counts)
print("Wednesday (Count) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")
mean = np.mean(thu_recomb_counts)
sd = np.std(thu_recomb_counts)
print("Thursday (Count) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")
mean = np.mean(fri_recomb_counts)
sd = np.std(fri_recomb_counts)
print("Friday (Count) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")

mean = np.mean(mon_recomb_percents)
sd = np.std(mon_recomb_percents)
print("Monday (Percent) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")
mean = np.mean(tue_recomb_percents)
sd = np.std(tue_recomb_percents)
print("Tuesday (Percent) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")
mean = np.mean(wed_recomb_percents)
sd = np.std(wed_recomb_percents)
print("Wednesday (Percent) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")
mean = np.mean(thu_recomb_percents)
sd = np.std(thu_recomb_percents)
print("Thursday (Percent) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")
mean = np.mean(fri_recomb_percents)
sd = np.std(fri_recomb_percents)
print("Friday (Percent) Mean: " + str(mean) + " SD: " + str(sd) + " Mean±2SD Interval: [" + str(mean - 2*sd) + ", " + str(mean + 2*sd) + "]")

print("Weekend Articles Count: " + str(weekend_article_count))
print("First Day: " + str(first_day))
print("Last Day: " + str(last_day))
