from pybit import usdt_perpetual
import credentials
import requests

session_auth = usdt_perpetual.HTTP(
                endpoint="https://api.bybit.com",
                api_key=credentials.BB_KEY,
                api_secret=credentials.BB_SECRET
            )

"""
Additional Functions for the Dashboard and conditions to check for before executing trades (Bybit in this case)
"""
# Get Total Position Margins for all active trades
def getTotalMargin():
    positions = session_auth.my_position()
    position_margin_sum = 0
    for i, data in enumerate(positions['result']):
        symbol = positions['result'][i]['data']['symbol']
        position_value = round(data['data']['position_value'], 2)
        position_margin = round(positions['result'][i]['data']['position_margin'], 2)
        if position_value > 0:
            position_margin_sum += position_margin
    return (round(position_margin_sum, 2))

# Get Value of Wallet so we can't execute trades below a threshhold or if our balance is less than our ordersize
def getWalletValue():
    balance = session_auth.get_wallet_balance(coin='USDT') # get your USDT balance
    wallet = round(balance['result']['USDT']['equity'], 2)
    return wallet

# Get the Top 10 Movers and Top 10 Losers to be displayed on dashboard
def getChange24h():
    endpoint = "https://api.bybit.com/v2/public/tickers"
    params = {"price24hPcnt": True}
    response = requests.get(endpoint, params=params)

    # Parsing the 24-hour percentage changes for each ticker
    tickers = response.json()["result"]
    changes = [(ticker["symbol"], float(ticker["price_24h_pcnt"])) for ticker in tickers]
    changes.sort(key=lambda x: x[1], reverse=True)

    # Top 10 winners
    winners = []
    for i in range(10):
        symbol = changes[i][0]
        price_change_24h = round(changes[i][1] * 100, 2)
        winners.append((symbol, price_change_24h))

    # Top 10 losers
    changes.sort(key=lambda x: x[1])
    losers = []
    for i in range(10):
        symbol = changes[i][0]
        price_change_24h = round(changes[i][1] * 100, 2)
        losers.append((symbol, price_change_24h))

    return winners, losers

# Get active positions to be displayed on the dashboard
def getPositions():
    positions = session_auth.my_position()
    positions_list = []
    for data in positions['result']:
        position_value = round(data['data']['position_value'], 2)
        if position_value > 0:
            symbol = data['data']['symbol']
            side = data['data']['side']
            entry_price = round(data['data']['entry_price'], 2)
            position_margin = round(data['data']['position_margin'], 2)
            leverage = data['data']['leverage']
            unrealised_pnl = round(data['data']['unrealised_pnl'], 2)
            
            # Amend this to display whatever you prefer
            positions_list.append({
                'symbol': symbol,
                'position_value': position_value,
                'side': side,
                'entry_price': entry_price,
                'position_margin': position_margin,
                'leverage': leverage,
                'unrealised_pnl': unrealised_pnl
            })
    return positions_list

# Get the last 3 transactions all symbols in symbols list
def getTransactions(symbol):
    for symbol in symbols:
        transactions = session_auth.public_trading_records(symbol=symbol)
        recent_3 = transactions['result'][:3]
        for order in recent_3:
            time = order['time']
            symbol = order['symbol']
            price = order['price']
            qty = order['qty']
            side = order['side']
            print(f"Time: {time}, Symbol: {symbol}, Price: {price}, Qty: {qty}, Side: {side}")

# Add the symbols that you regularly trade/ run strategies on to get transaction history
symbols = ['BTCUSDT', 'ETHUSDT', 'MATICUSDT', 'FTMUSDT', 'OPUSDT']



