import datetime as dt
import itertools
import json
import os
import sys
import threading
import time
from logging import exception

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests
from dateutil.relativedelta import relativedelta

'''
Simple Moving Average

SMA = (A(1) + A(2) + A(3) + ... + A(n)) / n

A = average in period n
n = number of time periods

Get all market data from 200 days before last day in weekdays list

'''


start = time.time()


class AlpacaServiceError(Exception):
    def __init__(self, message):
        super().__init__(message)


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + dt.timedelta(n)


def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rCalculating Simple Moving Averages ' + c)
        sys.stdout.flush()
        time.sleep(0.2)
    sys.stdout.write('\rDone!                                                ')


def calculate_sma(days, weekdays_list, sym_data):
    dic = {}
    i = 0
    for date in weekdays_list:
        sum = 0
        for j in range(i, days + i):
            sum += sym_data[j]['c']
        i += 1
        avg = sum / days
        dic[date] = avg
    return dic


done = False
t = threading.Thread(target=animate)
t.start()

symbol = 'INTC'

# Make list of holidays to get rid of between today and a year ago
# https://www.marketbeat.com/stock-market-holidays/
holidays_list = [dt.date(2020, 1, 1), dt.date(2020, 1, 20), dt.date(2020, 2, 17), dt.date(2020, 4, 10), dt.date(2020, 5, 25), dt.date(2020, 7, 3), dt.date(2020, 9, 7), dt.date(2020, 11, 26), dt.date(
    2020, 12, 25), dt.date(2021, 1, 1), dt.date(2021, 1, 18), dt.date(2021, 2, 15), dt.date(2021, 4, 2), dt.date(2021, 5, 31), dt.date(2021, 7, 5), dt.date(2021, 9, 6), dt.date(2021, 11, 25), dt.date(2021, 12, 24)]

today = dt.date.today()
year_ago = (today - relativedelta(years=1))
weekdays = []

# Get list of weekday dates
for date in daterange(year_ago, today):
    weekno = date.weekday()
    if weekno < 5:
        weekdays.append(date)

# Remove holidays
for date in holidays_list:
    if date in weekdays:
        weekdays.remove(date)

# Get all data need to calculate 200 day and 50 day moving averages for last year of market data

url = "https://data.alpaca.markets/v1/bars/day?symbols=" + symbol + \
    "&limit=" + str(200 + len(weekdays)) + "&until=" + \
    str(today) + "T23:59:59Z"
payload = {}
headers = {
    'APCA-API-KEY-ID': 'PKQLL80ZK3WGK3GF5S6D',
    'APCA-API-SECRET-KEY': 'EiKYfBhDHhnAtHdRPm3PDZ59sP6Kpvwrdqbx1qX1'
}

response = requests.request("GET", url, headers=headers, data=payload)

if response.status_code != 200:
    raise AlpacaServiceError(response.reason)

data = json.loads(response.text)

symbol_data = data[symbol]
symbol_data.reverse()

sma200_dic = calculate_sma(200, weekdays, symbol_data)
sma50_dic = calculate_sma(50, weekdays, symbol_data)

symbol_close = []
for i in range(len(weekdays)):
    symbol_close.append(symbol_data[i]['c'])


# Get ready to plot
dates = list(sma200_dic.keys())
sma200 = list(sma200_dic.values())
sma50 = list(sma50_dic.values())

fig = plt.figure(figsize=(12, 10))

# Start plotting
plt.title('Simple Moving Average - ' + symbol)
plt.xlabel("Time (Days)")
plt.ylabel("Price $")

plt.plot(dates, sma200, "-b", label="200 Day")
plt.plot(dates, sma50, "-r", label="50 Day")
plt.plot(dates, symbol_close, "-g", label="Closing Prices")

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=25))
plt.gca().set_xlim(dates[0], dates[-1])
plt.gcf().autofmt_xdate()

plt.legend(loc="upper left")
plt.grid()

done = True
plt.show()
os._exit(1)