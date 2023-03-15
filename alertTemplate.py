import json
import credentials

"""
Example Output:

{
'passphrase': 'passphrase', 
'TradeType': 'SWING', 
'OrderType': 'B1', 
'EntryPrice': 19700, 
'StopLoss': '5', 
'TakeProfit': '24500', 
'OrderSymbol': 'BTC'
}

"""

# Create quick alert templates here which you can paste into TradingView
myOrder = {
    "passphrase": credentials.WEBHOOK_PASSPHRASE,
    "OrderType": input("Order Type? (B1/S1) "),
    "TradeType": input("TradeType"),
    "EntryPrice": float(input("Entry Price? ")),
    "StopLoss": float(input("Stop Loss? (*% not Value*) ")),
    "TakeProfit": float(input("Take Profit? ")),
    "OrderSymbol": input("Symbol? (exclude USDT) "),
}

# Convert the dictionary to a JSON string with double quotation marks
json_string = json.dumps(myOrder)

# Print the JSON string
print(json.dumps(myOrder, indent=4))


