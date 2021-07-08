from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd 
import time
from selenium.webdriver.common.keys import Keys
from statistics import mean
import numpy as np
import math
import csv
import datetime
import yfinance as yf

def getResults(date, pre_or_post):  
 
    newrows = []
    resultsrows = []
    filename = "stocks_" + str(date) + ".csv"

    monthNum = date.strftime("%m")
    day = date.strftime("%d")
    year = date.strftime("%Y")
    dow = date.isoweekday()
    
    if str(pre_or_post) == "Pre":
        if dow == 1:
            threeDayPrevious = date + datetime.timedelta(days=-3)
            oMonthNum = threeDayPrevious.strftime("%m")
            oDay = threeDayPrevious.strftime("%d")
            oYear = threeDayPrevious.strftime("%Y")
        else:
            oneDayPrevious = date + datetime.timedelta(days=-1)
            oMonthNum = oneDayPrevious.strftime("%m")
            oDay = oneDayPrevious.strftime("%d")
            oYear = oneDayPrevious.strftime("%Y")

        startDate = str(oYear) + "-" + str(oMonthNum) + "-" + str(oDay)
        endDate = str(year) + "-" + str(monthNum) + "-" + str(day)
            
    else:
        if dow == 5:
            threeDayFuture = date + datetime.timedelta(days=3)
            oMonthNum = threeDayFuture.strftime("%m")
            oDay = threeDayFuture.strftime("%d")
            oYear = threeDayFuture.strftime("%Y")
        else:
            oneDayFuture = date + datetime.timedelta(days=1)
            oMonthNum = oneDayFuture.strftime("%m")
            oDay = oneDayFuture.strftime("%d")
            oYear = oneDayFuture.strftime("%Y")

        startDate = str(year) + "-" + str(monthNum) + "-" + str(day)
        endDate = str(oYear) + "-" + str(oMonthNum) + "-" + str(oDay)


    with open(str(filename), mode='r') as preresults_file:
        csv_reader = csv.reader(preresults_file)
        
        for row in csv_reader:
            pre_post = row[2]
            stock = row[0]

            if str(pre_post) == str(pre_or_post):

                stockData = yf.download(str(stock),start=str(startDate),end=str(endDate))
                
                opens = stockData['Open']
                closes = stockData['Close']

                dopen = opens[1]
                dclose = closes[1]
                pclose = closes[0]

                #Calculate %change at open and close
                changeopen = (float(dopen) - float(pclose)) / float(pclose)
                changeclose = (float(dclose) - float(pclose)) / float(pclose)

                #Figure out result of predictions
                if (changeopen > 0 and str(row[7]) == "Buy") or (changeopen < 0 and str(row[7]) == "Short"):
                    openresult = "Correct"
                elif str(row[7]) == "n/a" or str(row[7]) == "Do nothing":
                    openresult = "n/a"
                else:
                    openresult = "Incorrect"

                if (changeclose > 0 and str(row[7]) == "Buy") or (changeclose < 0 and str(row[7]) == "Short"):
                    closeresult = "Correct"
                elif str(row[7]) == "n/a" or str(row[7]) == "Do nothing":
                    closeresult = "n/a"
                else:
                    closeresult = "Incorrect"
                
                row = row + [pclose, dopen, openresult, changeopen, dclose, closeresult, changeclose]
                resultsrows.append([row[0], row[1], row[5], row[6], row[7], pclose, dopen, openresult, changeopen, dclose, closeresult, changeclose])

            newrows.append(row)

    
    with open(str(filename), mode='w', newline='') as results_file:
        csv_writer = csv.writer(results_file)
        #csv_writer.writerow(headers)

        for row in newrows:
            csv_writer.writerow(row)

    appendToMasterResultsFile(resultsrows)

def appendToMasterResultsFile(rows):
    with open('masterResultsFile.csv','a',newline='') as resultsfile:
        csv_writer = csv.writer(resultsfile)
        for row in rows:
            csv_writer.writerow(row)

driver = webdriver.Chrome("C:/Users/Matt/Desktop/stockwebscraper/chromedriver")

stocks = []
dates = []
cEPS = []
lEPS = []
pre_post = []
slopes = []
eps_change = []
buy_short = []
clean_stocks = []
clean_dates = []
clean_cEPS = []
clean_lEPS = []
clean_pre_post = []

#Earnings data gathering and cleaning up
driver.get("https://old.nasdaq.com/earnings/earnings-calendar.aspx")
today = datetime.date.today()
two_days_ago = today + datetime.timedelta(days=-2)
three_days_ago = today + datetime.timedelta(days=-3)
tomorrow = today + datetime.timedelta(days=1)
month = tomorrow.strftime("%b")
day = tomorrow.strftime("%d")
year = tomorrow.strftime("%Y")
monthNum = tomorrow.strftime("%m")

#driver.get("https://old.nasdaq.com/earnings/earnings-calendar.aspx?date=" + str(year) + "-" + str(month) + "-" + str(day))
content = driver.page_source
soup = BeautifulSoup(content)
stocks = soup.select("td:nth-of-type(2)")
dates = soup.select("td:nth-of-type(3)")
cEPS = soup.select("td:nth-of-type(5)")
lEPS = soup.select("td:nth-of-type(8)")
pre_post = soup.find_all(alt={'Pre-Market Quotes', 'After Hours Quotes'})

#Cleans up stock tickers
for stock in stocks:
    b = str(stock).find('earnings/report/')
    e = str(stock).find('\" id=')
    if b != -1 and e != -1:
        clean_stocks.append(str(stock)[b+16:e])
        

#Cleans up date of earnings
for date in dates:
    s = str(date).find('/')
    d = str(date)[s-2:s+8]
    t = str(d).find('2')
    if s != -1 and t != -1:
        clean_dates.append(str(d))

#Cleans up consensus EPS
for ceps in cEPS:
    d = str(ceps).find('$')
    n = str(ceps).find('\n', 10)
    if d != -1 and n != -1:
        clean_cEPS.append(str(ceps)[d+1:n])

#Cleans up last year's EPS
for leps in lEPS:
    d = str(leps).find('$')
    n = str(leps).find('\n', 10)
    if d != -1 and n != -1:
        clean_lEPS.append(str(leps)[d+1:n])

#Cleans up pre or post market
for pp in pre_post:
    pre = str(pp).find('Pre')
    post = str(pp).find('After')
    if pre != -1:
        clean_pre_post.append("Pre")
    if post != -1:
        clean_pre_post.append("Post")


#Stock by stock price gathering
for stock in clean_stocks:

    oneYearAgo = int(year) - 1

    startDate = str(oneYearAgo) + "-" + str(monthNum) + "-" + str(day)
    endDate = str(year) + "-" + str(monthNum) + "-" + str(day)

    stockData = yf.download(str(stock),start=str(startDate),end=str(endDate))
    clean_closes = stockData['Close']

    #Calculates slope of best fit line
    x = list(range(len(clean_closes)))
    xs = np.array(x, dtype=np.float64)
    ys = np.array(clean_closes, dtype=np.float64)
    try:
        m = (((mean(xs)*mean(ys)) - mean(xs*ys)) / ((mean(xs)*mean(xs)) - mean(xs*xs)))

        #flips sign and shifts decimal place
        before_dec, after_dec = str(m).split('.')
        m = float('.'.join((before_dec, after_dec[0:5]))) * -10
        slopes.append(m)
    except:
        slopes.append(-999)

#Calculate percentage change in EPS
for i in range(len(clean_cEPS)):

    changep = 0

    #Both values are positive
    try:
        if float(clean_cEPS[i]) > 0 and  float(clean_lEPS[i]) > 0:
            changep = (float(clean_cEPS[i]) - float(clean_lEPS[i])) / float(clean_lEPS[i])

        #Both values are negative
        elif float(clean_cEPS[i]) < 0 and  float(clean_lEPS[i]) < 0:
            changep = (float(clean_cEPS[i]) - float(clean_lEPS[i])) / abs(float(clean_lEPS[i]))

        #Consensus EPS is negative and last EPS is positive
        elif float(clean_cEPS[i]) < 0 and  float(clean_lEPS[i]) > 0:
            changep = (float(clean_cEPS[i]) - float(clean_lEPS[i])) / float(clean_lEPS[i])

        #Consensus EPS is postive and last EPS is negative
        elif float(clean_cEPS[i]) > 0 and  float(clean_lEPS[i]) < 0:
            changep = (float(clean_cEPS[i]) - float(clean_lEPS[i])) / abs(float(clean_lEPS[i]))
            
        before_dec, after_dec = str(changep).split('.')
        changep = float('.'.join((before_dec, after_dec[0:5])))
        eps_change.append(changep)
    except:
        eps_change.append("n/a")

#Makes decisions on what to do with each stock based on eps change and slope of best fit line
for i in range(len(eps_change)):

    try:
        if float(eps_change[i]) > 0 and float(slopes[i]) > 0:
            choice = "Short"
        elif float(eps_change[i]) < 0 and float(slopes[i]) < 0:
            choice = "Buy"
        else:
            choice = "Do nothing"

        buy_short.append(choice)
    except:
        buy_short.append("n/a")

#Creates new file with today's date and writes all data and results to it
filename = "stocks_" + str(tomorrow) + ".csv"
csv_writer = csv.writer(open(filename, 'w', newline=''))

headers = ['Stock Ticker', 'Date', 'Pre/Post', 'Last EPS', 'Consensus EPS', 'EPS % Change', 'Slope of best fit', 'Decision', 'Previous Close', 'Open price', 'Open Result', '% Change Open', 'Close price', 'Close Result', '% Change Close']
csv_writer.writerow(headers)

for i in range(len(clean_stocks)):
    row = [clean_stocks[i], clean_dates[i], clean_pre_post[i], clean_lEPS[i], clean_cEPS[i], eps_change[i], slopes[i], buy_short[i]]
    csv_writer.writerow(row)

try:
    getResults(two_days_ago, "Pre")
except:
    error = open("error_" + str(two_days_ago) + ".txt", "a")

try:
    getResults(three_days_ago, "Post")
except:
    error = open("error_" + str(three_days_ago) + ".txt", "a")
    error.write("error with post results\n")

#Closes driver
driver.close()