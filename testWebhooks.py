from flask import Flask, render_template, request
import credentials, json, requests, datetime
from pybit import usdt_perpetual

# When making different pinescript strategies, use this script to test webhooks locally without actually executing trade
app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    webhook_message = json.loads(request.data)
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    print(f'|| {current_time} || incoming webhook || {webhook_message} ||')
    
    if webhook_message['passphrase'] != credentials.WEBHOOK_PASSPHRASE:
        return json.dumps({
            'code': 'error',
            'message': 'nice try buddy'
        })
    print('Scraping Order')
    orderType = webhook_message['OrderType']
    tradeType = webhook_message['TradeType']
    entryPrice = float(webhook_message['EntryPrice'])
    orderSymbol = webhook_message['OrderSymbol'] + 'USDT'
    stopLossPct = float(webhook_message['StopLoss']) + 0.5
    takeProfit = float(webhook_message['TakeProfit'])

    side = "Buy" if "B" in orderType else "Sell"

    print(tradeType, orderType, entryPrice, stopLossPct, takeProfit, orderSymbol, side)
    
    return json.dumps({
        'code': 'success',
        'message': 'webhook received and processed'
    })

if __name__ == '__main__':
    app.run()

