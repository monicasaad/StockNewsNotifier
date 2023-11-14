# required imports
import requests
from datetime import datetime, timedelta
import os
from twilio.rest import Client

# constants
STOCK = 'TSLA'
COMPANY_NAME = 'Tesla Inc'
ALPHA_VANTAGE_API = '' #stock key
NEWS_API = '' #news key
ACCOUNT_SID = ""  # twillio key
AUTH_TOKEN = os.environ.get("TWILLIO_AUTH_TOKEN")

STOCK_ENDPOINT = 'https://www.alphavantage.co/query'
NEWS_ENDPOINT = 'https://newsapi.org/v2/everything'

# stock parameters
parameters = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK,
    'apikey': ALPHA_VANTAGE_API
}

if datetime.now().weekday() == 5:  # if current weekday is Saturday
    today_date = str(datetime.now().date() - timedelta(1))  # stock market numbers don't update on weekends, use data for Friday
    yesterday_date = str(datetime.now().date() - timedelta(2))  # get hold of current date and subtract 1 day to get yesterday's date
elif datetime.now().weekday() == 6:  # if current weekday is Sunday
    today_date = str(datetime.now().date() - timedelta(2))
    yesterday_date = str(datetime.now().date() - timedelta(3))  # get hold of current date and subtract 1 day to get yesterday's date
else:
    today_date = str(datetime.now().date())
    yesterday_date = str(datetime.now().date() - timedelta(1))  # get hold of current date and subtract 1 day to get yesterday's date

# get stock data
response = requests.get(url=STOCK_ENDPOINT, params=parameters)
response.raise_for_status()
response = response.json()
stock_data = response['Time Series (Daily)']

# get a hold of closing stock price for today and yesterday
today_closing = float(stock_data[today_date]['4. close'])
yesterday_closing = float(stock_data[yesterday_date]['4. close'])

# find positive difference and check if stock price went up or down more than 5%
up_down = None  # variable to hold symbol whether stoke rose or dropped
difference = today_closing - yesterday_closing
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"
five_percent = yesterday_closing * 0.05

# if stock rose OR dropped more than 5%, fetch first 3 articles for the COMPANY_NAME
if abs(difference) >= five_percent:

    parameters = {
        'qInTitle': COMPANY_NAME,
        'apiKey': NEWS_API
    }

    response = requests.get(url=NEWS_ENDPOINT, params=parameters)
    response.raise_for_status()
    response = response.json()

    first_3_articles = response['articles'][:3]

    articles_list = [f"Headline: {article['title']}.\nBrief:{article['description']}" for article in first_3_articles]

    # send text message notifications using twilio
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    # message for sms notification
    for article in articles_list:
        message = client.messages \
            .create(
                body=f"{STOCK}: {up_down}{int(abs(difference))}%\n{article}",
                from_="+12121212121", #twilio number
                to="+11234567890" #forwarding phone number
            )

        # print status (queued means successful)
        print(message.status)
