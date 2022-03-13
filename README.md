<h1 align='center'>
  🍋 Financial News Trader 🍋 
</h1>

## 👋 Introduction 

This is a public [lemon.markets](https://lemon.markets) repository that outlines a **sentiment analysis strategy** using our API. To get a general understanding of the API, please refer to our [documentation](https://docs.lemon.markets). The `financial-news-trader` scrapes headlines found on [MarketWatch.com](https://www.marketwatch.com/), performs sentiment analysis using VADER and places trades depending on the direction of the sentiment. Note that this is only a showcase of the product and should not be used as investment advice. 

A walk-through of this script can be found in [this blog-post](https://medium.com/lemon-markets/automated-news-following-trading-strategy-using-sentiment-analysis-5940e86e4333).

## 🏃‍♂️ Quick Start
Not interested in reading a novella before you get started? We get it! To get this project up and running quickly, here's what you need to do:
1. Clone this repository;
2. Sign up to [lemon.markets](https://www.lemon.markets/) and [OpenFIGI](https://www.openfigi.com/user/signup);
3. Configure your environment variables as outlined in the 'Configuration' section;
4. Modify the trade logic in the `headlines.py` file;
5. Update list of tickers you wish to ignore in the `headlines.py` file;
6. Update the parameters (e.g. `quantity`) in the `helpers.py` file;
7. Run the script & see how it performs! 

## 😊😢 Sentiment Analysis?!
'Sentiment' is a view or opinion about a particular topic - if we analyse the sentiment expressed in a news article about a financial instrument, we want to determine whether it is positive or negative. For example, the headline "Pelaton Earnings Disappointed. Another Pandemic Play Sinks." (real headline collected on 05-11-2021) clearly tells us that a long position in Pelaton probably isn't a good move. We can make this kind of judgement based off of the words 'disappointed' and 'sinks'. However, we'd like to automate this process, so we're going to use [VADER](https://medium.com/analytics-vidhya/simplifying-social-media-sentiment-analysis-using-vader-in-python-f9e6ec6fc52f), which is a lexicon of words along with their 'sentiment scores'. A headline will be analysed based on its polarity (postivie or negative) and intensity of emotion, which results in a score between -1 (very negative) and +1 (very positive). We can then make trade decisions based on these scores.

## 🔌 API Usage

This project uses the [lemon.markets API](https://www.lemon.markets/en-de/for-developers) and the [OpenFIGI API](https://www.openfigi.com/api).

lemon.markets is a brokerage API by developers for developers that allows you to build your own experience at the stock market. We will use the Market Data API and Trading API to retrieve the ISIN (unique identifier) that belongs to a particular financial instrument and to place trades. If you do not have a lemon.markets account yet, you can sign up [here](https://www.lemon.markets/waitlist). 🚀

OpenFIGI allows the mapping of third-party symbologies to FIGIs, which is a universal naming convention for financial instruments. We will use the API to map a ticker (American standard) to an ISIN (European standard). You can check out [this](https://medium.com/lemon-markets/mapping-a-ticker-symbol-to-isin-using-openfigi-lemon-markets-9c60a8892ee5) article to learn more. If you do not have an OpenFIGI account yet, you can sign up [here](https://www.openfigi.com/user/signup). 

## ⚙️ Configuration

The script uses several environment variables, configure your .env file as follows:

```python
MIC=XMUN
TRADING_URL=https://paper-trading.lemon.markets/v1/
MARKET_URL=https://data.lemon.markets/v1/
API_KEY=<your-api-key>
OPENFIGI_URL=https://api.openfigi.com/v3/search/
OPENFIGI_KEY=<your-openfigi-key>
```
Please provide your unique `API_KEY` and `OPENFIGI_KEY`.

## ❓ What's happening under the hood?
### 📊 Collecting Data
For this project, we are collecting data from MarketWatch because the data is presented in an easily digestible format. For each headline, we are given its date and the ticker(s) corresponding to the headline. To collect the headlines, we use a simple GET request against the desired URL:
```
import requests
page = requests.get("https://marketwatch.com/investing/technology")
```
Then, to parse the data, we use [BeautifulSoup](https://medium.com/r?url=https%3A%2F%2Fwww.crummy.com%2Fsoftware%2FBeautifulSoup%2Fbs4%2Fdoc%2F), which is a Python package that can extract data from HTML documents. We collect the headline, the date of publication and the associated ticker(s). 

### 👩‍🏭 Pre-processing the Data
At this stage, it's likely your data needs some (additional) pre-processing before it's ready for sentiment analysis and trading. Luckily, in our case, we don't have to do a lot of pre-processing. We removed any headlines without tickers and headlines with tickers that we know are not tradable on lemon.markets (to make the dataset smaller). To do this, we created a list of non-tradable tickers and constructed a new DataFrame of the collected headlines, filtered by the negation of the above list. Additionally, to trade on lemon.markets, we need to obtain the instrument's ISIN. Because we trade on a German exchange, querying for a US ticker will not (always) result in the correct instrument. Therefore, to ensure that there are no compatibility issues, we suggest mapping a ticker to its ISIN before trading (using OpenFIGI).

### 😃 Performing Sentiment Analysis 
We use VADER to perform sentiment analysis on all collected headlines as follows:
``` python
from nltk.sentiment.vader import SentimentIntensityAnalyzer

vader = SentimentIntensityAnalyzer()

scores = []

for headline in headlines_df.loc[:,"headline"]:
    score = vader.polarity_scores(headline).get("compound")
    scores.append(score)
    
headlines_df.loc[:,"score"] = scores
```
### 📈 Placing Trades 
Our base project works with a very simple trade rule: buy any instrument with a score above 0.5 and sell any instrument with a score below -0.5 (see if you can come up with something a bit more complex 😉):
``` python
buy = []
sell = []

for index, row in headlines_df.iterrows():
    if row['score'] > 0.5 and row['isin'] != 'No ISIN found':
        buy.append(row['isin'])
    if row['score'] < -0.5 and row['isin'] != 'No ISIN found':
        sell.append(row['isin'])
```
We can then feed this list of ISINs to the lemon.markets API to place and activate our trades. 

## 🤝 Interested in contributing?

This (and all lemon.markets open source projects) is(are) a work in progress. If you are interested in contributing to this repository, simply create a PR and/or contact us at [support@lemon.markets](mailto:support@lemon.markets).

Looking forward to building lemon.markets with you 🍋

