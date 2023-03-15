from emailScraper import Scraper
from orderExecutor import orderExecutor

def algoTrader():

    position_details_list = Scraper()
    def process_position_details(position_details):
        print(f'Alert Triggered: {position_details}')

    # Iterate over the list of dictionaries
    for position_details in position_details_list:
        process_position_details(position_details)

        orderType = position_details['OrderType']
        entryPrice = float(position_details['EntryPrice'])
        stopLoss = float(position_details['StopLoss'])
        takeProfit = float(position_details['TakeProfit'])
        orderSymbol = position_details['Symbol'] + 'USDT'

        orderExecutor(orderType, entryPrice, stopLoss, takeProfit, orderSymbol)

    if not position_details_list:
        print('No Alerts Found')
