import credentials
from pybit import usdt_perpetual

session_auth = usdt_perpetual.HTTP(
        endpoint="https://api.bybit.com",
        api_key=credentials.KEY,
        api_secret=credentials.SECRET
        )

def orderExecutor(orderType, entryPrice, stopLoss, takeProfit, orderSymbol):

    SL_PCT_FUNCS = {
        'B1': lambda e, s: round((e / s - 1), 3) * 100,
        'B3': lambda e, s: round((e / s - 1), 3) * 100,
        'S1': lambda e, s: round((s / e - 1), 3) * 100,
        'S3': lambda e, s: round((s / e - 1), 3) * 100
    }

    def calc_sl_pct(orderType, entryPrice, stopLoss):
        func = SL_PCT_FUNCS.get(orderType)
        return func(entryPrice, stopLoss) if func else None

    sl_pct = round(calc_sl_pct(orderType, entryPrice, stopLoss), 3)
    if sl_pct is None:
        sl_pct = 1
    else:
        sl_pct = max(sl_pct, 1)

    # Setting Leverage
    MAX_LEVERAGE = {
        'BTCUSDT': 100,
        'ETHUSDT': 100,
    }

    def max_leverage(symbol):
        return MAX_LEVERAGE.get(symbol, 50)

    leverage = round((max_leverage(orderSymbol) / sl_pct), 2)
    positionDetails = session_auth.my_position(symbol=orderSymbol)
    positionInfo = (positionDetails['result'])[0]['leverage']

    if positionInfo != leverage:
        try:
            session_auth.set_leverage(symbol=orderSymbol, buy_leverage=leverage, sell_leverage=leverage)
        except:
            try:
                leverage = 25
                session_auth.set_leverage(symbol=orderSymbol, buy_leverage=leverage, sell_leverage=leverage)
            except:
                print('Unable to Set Leverage')


    # Can adjust order size as well like this
    # dictionary that maps order types to order sizes
    ORDER_SIZES = {
        'B1': 20,
        'B3': 20,
        'S1': 20,
        'S3': 20
    }
    # Get the order size for the given order type
    orderSize = ORDER_SIZES.get(orderType, 20)
    orderQty = round(((orderSize * leverage) / (entryPrice)), 3)

    # so if orderType is B1:
    # orderType = 'B1'
    # orderSize = ORDER_SIZES.get(orderType, 20)
    # print(orderSize)  # Output: 20
    # If there is no orderSize given, then the default is 20. 

    def place_order(side, orderQty, entryPrice, orderSymbol, takeProfit, stopLoss):
            session_auth.place_active_order(
            symbol=orderSymbol,
            side=side,
            order_type="Limit",
            qty=orderQty,
            price=entryPrice,
            take_profit=takeProfit,
            stop_loss=stopLoss,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False
        )

    # Place a single buy order
    def B1(orderQty, entryPrice, orderSymbol, takeProfit, stopLoss):
        place_order("Buy", orderQty, entryPrice, orderSymbol, takeProfit, stopLoss)
        print(
            '------------------------------------------------------------------------', '\n'
            'Order to buy', str(orderQty), 'of', positionDetails['result'][0]['symbol'], 'has been set.', '\n'
            'Entry: ' + str(entryPrice), '| SL: ' + str(stopLoss), '| TP: ' + str(takeProfit), '\n'
            'Leverage:', str(leverage) + 'x', '| SL:', str(sl_pct) + '%', '\n'
            '------------------------------------------------------------------------', '\n'
        )

    def S1(orderQty, entryPrice, orderSymbol, takeProfit, stopLoss):
        place_order("Sell", orderQty, entryPrice, orderSymbol, takeProfit, stopLoss)
        print(
            '------------------------------------------------------------------------', '\n'
            'Order to sell', str(orderQty), 'of', positionDetails['result'][0]['symbol'], 'has been set.', '\n'
            'Entry: ' + str(entryPrice), '| SL: ' + str(stopLoss), '| TP: ' + str(takeProfit), '\n'
            'Leverage:', str(leverage) + 'x', '| SL:', str(sl_pct) + '%', '\n'
            '------------------------------------------------------------------------', '\n'
        )
    order_type_map = {
        'B1': B1,
        'S1': S1,
    }

    def execute_order(order_type, orderQty, entryPrice, orderSymbol, takeProfit, stopLoss):
        # Get the function corresponding to the given order type
        func = order_type_map.get(order_type)

        # If the function exists, call it
        if func:
            func(orderQty, entryPrice, orderSymbol, takeProfit, stopLoss)
        else:
            print('Error Executing Order, Please Recheck Inputs')

    execute_order(orderType, orderQty, entryPrice, orderSymbol, takeProfit, stopLoss)