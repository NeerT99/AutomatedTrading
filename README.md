# Trading Tools

The Goal of this repository is to create a script that will automate my trading. The repository contains multiple scripts all with different purposes. The details of each script is given below. Please be careful as some of these scripts involve the use of high leverage trading and this is not advised!

Be aware that this works for my strategy, and is not advised as it is highly risky!!!
for example, trading BTC at 100x leverage means that a 1% move would wipe out your whole position on that trade!
If you would like to lower the risk, change the leverage values and order sizes to match your level of risk.

Quick Execute:
--------------------
This is not an automated script but rather a manual script which you can use to instantly set a limit order on bybit from the terminal itself.
note: This script maximises leverage given order size and stoploss so manage risk carefully.

The Automated Trader:
---------------------
This script uses alerts set on TradingView to execute trades on bybit.
The way the script works is as follows:
  1. Input your trade strategy into pinescript in TradingView. Use the alert template file to create an alert with the correct format.
  2. When an alert goes off in TradingView, an email is sent to your outlook email. 
  3. The Scraper function will scrape the email from outlook for details of the trade - order type, symbol, entry, stop loss and take profit levels.
  4. The OrderExecutor function then takes these details as input in order to execute the trades using bybit api. 
  note: S1 indicates a single limit sell order. An S3 order is a sell limit order split into 3 around the entry price. 
  5. The algo file runs an infinite loop that scrapes the outlook inbox constantly over specified intervals. Each email will execute a trade.

Gathering Data: (In Progress***)
--------------------- 
the getCMCdata script will:
  1. use the selenium library to access coinmarketcap
  2. print all the top winners and losers from the last 1h, 24hrs and 7d
 
the getCMCdata script will pick the top winners to long, and the top losers to short in order to maximise profits.
The idea behind this is to use other sources of data (for example economic data such as CPI and NFP) to decide whether to long or short and use this script to long the strongest coins and/or short the weakest depending on the data. 
