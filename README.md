# Analysis-and-Research

The Goal of this repository is to create a script that will automate my trading. The repository contains multiple scripts all with different purposes. The details of each script is given below. Please be careful as some of these scripts involve the use of high leverage trading and this is not advised!

the getCMCdata script will:
  1. use the selenium library to access coinmarketcap
  2. print all the top winners and losers from the last 1h, 24hrs and 7d
 
The idea behind this is to use other sources of data (for example economic data such as CPI and NFP) to decide whether to long or short.
Then use the getCMCdata script to pick the top winners to long, and the top losers to short in order to maximise profits.

the QuickExecute script is a script designed to set a limit order on bybit from the terminal itself.
This script is using a strategy that maximises leverage given order size and stoploss.

Be aware that this works for my strategy, and is not advised as it is highly risky!!!
for example, trading BTC at 100x leverage means that a 1% move would wipe out your whole position on that trade!

