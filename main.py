import os

import requests
import datetime as dt
import smtplib

my_gmail = os.environ["MY_EMAIL"]
gmail_smtp = os.environ["SMTP"]
gpassword = os.environ["G_PASS"]

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
today = dt.datetime.today().strftime('%Y-%m-%d')

# STOCKS
OMW_Endpoint = "https://www.alphavantage.co/query"
API_KEY = os.environ["STOCK_API"]

parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "interval": "1min",
    "apikey": API_KEY
}

response = requests.get(OMW_Endpoint, params=parameters)
response.raise_for_status()
data = response.json()

open_price = float(data['Time Series (Daily)'][today]['1. open'])
close_price = float(data['Time Series (Daily)'][today]['4. close'])
daily_change = round(((close_price - open_price) / open_price) * 100, 2)
daily_change_string = f"{daily_change}%"

# NEWS
NEWS_Endpoint = "https://newsapi.org/v2/everything"
API_KEY = os.environ["NEWS_API"]

news_parameters = {
    "q": COMPANY_NAME,

    "language": "en",
    "apiKey": API_KEY
}

news_response = requests.get(NEWS_Endpoint, params=news_parameters)
news_response.raise_for_status()
news_data = news_response.json()

# Doing the price check and sending an email if conditions are met and news exists
if daily_change > 5 or daily_change < 5:
    try:
        headline1 = news_data['articles'][0]['title']
        brief1 = news_data['articles'][0]['content']
        message = f"Subject:{STOCK} {daily_change_string} \n\nHeadline: {headline1} \nBrief: {brief1}".encode()
        try:
            headline2 = news_data['articles'][1]['title']
            brief2 = news_data['articles'][1]['content']
            message = (f"Subject:{STOCK} {daily_change_string}\n\nHeadline: {headline1}\nBrief: {brief1}"
                       f"\n\nHeadline: {headline2}\nBrief: {brief2}").encode()
            try:
                headline3 = news_data['articles'][2]['title']
                brief3 = news_data['articles'][2]['content']
                message = (f"Subject:{STOCK} {daily_change_string}\n\nHeadline: {headline1}\nBrief: {brief1}"
                           f"\n\nHeadline: {headline2}\nBrief: {brief2}\n\nHeadline: {headline3}\nBrief: {brief3}").encode()
            except IndexError:
                pass
        except IndexError:
            pass
    except IndexError:
        pass
    else:
        print(message)
        with smtplib.SMTP(gmail_smtp) as connection:
            connection.starttls()
            # tls means transport layer security
            connection.login(user=my_gmail, password=gpassword)
            connection.sendmail(
                from_addr=my_gmail,
                to_addrs=my_gmail,
                msg=message
            )
