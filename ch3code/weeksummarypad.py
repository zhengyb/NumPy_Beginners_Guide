import numpy as np
from datetime import datetime

# Monday 0
# Tuesday 1
# Wednesday 2
# Thursday 3
# Friday 4
# Saturday 5
# Sunday 6


def datestr2num(s):
   return datetime.strptime(s, "%d-%m-%Y").date().weekday()

dates, open, high, low, close = np.loadtxt('data.csv', delimiter=',', usecols=(
    1, 3, 4, 5, 6), converters={1: datestr2num}, unpack=True)

dates_diff = np.diff(dates)
blank_idx1 = np.where((dates_diff == 1), -5, dates_diff)
print "Blank indices type1 is/are ", blank_idx1
blank_idx2 = np.where((blank_idx1 == -4), -5, blank_idx1)
print "Blank indices type2 is/are ", blank_idx2
blank_idx = np.where((blank_idx2 != -5))[0]
print "Blank indices is/are ", blank_idx

def pad_data_fun(blank_idx, d, o, h, l, c):
    d_pad = np.array([])
    o_pad = np.array([])
    h_pad = np.array([])
    l_pad = np.array([])
    c_pad = np.array([])
    last_idx = 0
    for i in blank_idx:
        print "idx ", i, " need to be paded"
        this_idx = i + 1
        d_pad = np.concatenate((d_pad, d[last_idx:this_idx]), axis=0)
        o_pad = np.concatenate((o_pad, o[last_idx:this_idx]), axis=0)
        h_pad = np.concatenate((h_pad, h[last_idx:this_idx]), axis=0)
        l_pad = np.concatenate((l_pad, l[last_idx:this_idx]), axis=0)
        c_pad = np.concatenate((c_pad, c[last_idx:this_idx]), axis=0)
        last_date = int(d[i])
        next_date = int(d[i + 1])
        print "Last Date:", last_date, " Next Date:", next_date
        if (next_date > last_date):
            pad_date = np.arange(range(last_date + 1, next_date))
        else:
            delta_date = next_date - last_date
            pad_date_cnt = delta_date - (-4)
            pad_date = np.arange(last_date + 1, last_date + pad_date_cnt + 1)
            pad_date = np.where(pad_date > 4, pad_date - 5, pad_date)

        zero_data = np.zeros(pad_date.size)
        infs_date = np.ones(pad_date.size) * float("inf")
        d_pad = np.concatenate((d_pad, pad_date), axis=0)
        o_pad = np.concatenate((o_pad, zero_data), axis=0)
        h_pad = np.concatenate((h_pad, zero_data), axis=0)
        l_pad = np.concatenate((l_pad, infs_date), axis=0)
        c_pad = np.concatenate((c_pad, zero_data), axis=0)

        last_idx = this_idx
    d_pad = np.concatenate((d_pad, d[this_idx:]), axis=0)
    o_pad = np.concatenate((o_pad, o[this_idx:]), axis=0)
    h_pad = np.concatenate((h_pad, h[this_idx:]), axis=0)
    l_pad = np.concatenate((l_pad, l[this_idx:]), axis=0)
    c_pad = np.concatenate((c_pad, c[this_idx:]), axis=0)
    return (d_pad, o_pad, h_pad, l_pad, c_pad)


def print_data_detail(d, o, h, l, c):
    print "datas: ", d
    print "open: ", o
    print "high: ", h
    print "low: ", l
    print "close: ", c

print "Data before paded"
print_data_detail(dates, open, high, low, close)
(dates, open, high, low, close) = pad_data_fun(
    blank_idx, dates, open, high, low, close)

#low = np.where(low == 0, float("inf"), low)

print "Data after paded"
print_data_detail(dates, open, high, low, close)

# get first Monday
first_monday = np.ravel(np.where(dates == 0))[0]
print "The first Monday index is", first_monday

# get last Friday
last_friday = np.ravel(np.where(dates == 4))[-1]
print "The last Friday index is", last_friday

weeks_indices = np.arange(first_monday, last_friday + 1)
print "Weeks indices initial", weeks_indices

weeks_cnt = (last_friday - first_monday + 1) / 5
splited_weeks_indices = np.split(weeks_indices, weeks_cnt)
print "Weeks indices after split", splited_weeks_indices


def summarize(a, o, h, l, c):
    wo = np.take(o, a)
    first_open = wo[np.where(wo > 0)[0][0]]
    week_high = np.max(np.take(h, a))
    week_low = np.min( np.take(l, a) )
    wc = np.take(c, a)
    last_close = wc[np.where(wc > 0)[0][-1]]

    return("APPL", first_open, week_high, week_low, last_close)

weeksummary = np.apply_along_axis(
    summarize, 1, splited_weeks_indices, open, high, low, close)
print "Week summary", weeksummary

np.savetxt("weeksummary_pad.csv", weeksummary, delimiter=",", fmt="%s")