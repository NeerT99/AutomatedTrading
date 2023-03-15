# Automated Trading
This repository provides an automated trading system that combines the alert feature of TradingView with a Flask app (via ngrok) to execute trades on Bybit and Binance exchanges.

TradingView is used to create either:

- Manual alerts.
- Pine Script strategies that output alerts.

Both of these will output an alert in a specific format. This alert is then sent to a ngrok server via webhook, which is locally tunneled to our Flask application. The Flask application parses the details of the webhook and executes the trades on Bybit and Binance. This approach is faster, more scalable, and secure compared to the previous system which relied on email scraping alerts every 5 minutes.

# Repository Contents
- credentials.py - Update this file to include your API keys for the desired exchanges.

- algo.py - The main script running the trading system. It contains the Flask application that receives and parses the webhook, and executes the trades. Comments are included throughout the file to explain each step.

- functions.py - This file supports algo.py by providing additional functions for the Dashboard and conditions to check before executing trades.

- dashboard.html - The trading dashboard that turns the local host into a trading dashboard, where you can observe your active positions, spot buys, an economic calendar, and live price data using TradingView widgets.

- trades.csv - Executed trades are logged into this file.

- testWebhooks.py - Use this script to test the output alerts from Pine Script strategies without actually executing trades.

- alertTemplate.py - This script allows you to quickly generate the alert template for manual alerts rather than automated strategies.

- BBMA and MRSI are examples of Pine Script strategies created to demonstrate how to create a Pine Script strategy and output the alert in the required format.

# Getting Started
Update the credentials.py file with your exchange API keys and customize the trading strategies in the algo.py file according to your preferences.
Run the algo.py file and use ./ngrok http 5000 in a separate terminal to connect your local host to ngrok. Copy the link of the ngrok server and paste the URL of the server follwed by /webhook in the webhook URL of the alert in tradingview like this -> "https:// xxxx-xxxx-xxxx-xxxx-xxxx-xxx-xxxx-xxxx-xxxx.eu.ngrok .io/webhook". 

# Contributing
Feel free to fork this repository, make changes, and submit pull requests. If you have any questions or suggestions, please open an issue.

# Disclaimer
This trading bot is provided for educational purposes only. It is not intended for live trading or as financial advice. The author and contributors assume no responsibility for any losses or damages incurred through the use of this code. Always conduct thorough research and backtesting before using any automated trading strategies.
