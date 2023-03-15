import credentials, json, time, csv, datetime
from flask import Flask, render_template, request
from pybit import usdt_perpetual
from binance.client import Client
from functions import getTotalMargin, getChange24h, getPositions, getWalletValue

app = Flask(__name__)

# Creating our Trading Dashboard
@app.route('/')
def dashboard():
    trades = []
    with open('trades.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            trades.append(row)

    # Run these functions everytime we refresh our dashboard
    winners, losers = getChange24h()
    positions = getPositions()

    return render_template('dashboard.html', trades=trades, winners=winners, losers=losers, positions=positions)

# This is where our TradingView webhooks are posted and parsed
@app.route('/webhook', methods=['POST'])
def webhookHandler():
    """
    This is an example of an incoming webhook:
    {'passphrase': 'passphrase', 'TradeType': 'BBMA', 'OrderType': 'B1', 'EntryPrice': 16500, 'StopLoss': '50', 'TakeProfit': '50', 'OrderSymbol': ' BTC'} ||
    """
    webhook_message = json.loads(request.data)
    print('INCOMING WEBHOOK: ', webhook_message)
    
    # Added security measure so that only the webhooks with the correct passphrase will be executed. 
    if webhook_message['passphrase'] != credentials.WEBHOOK_PASSPHRASE:
        return json.dumps({
            'code': 'error',
            'message': 'you really thought you did something there lmao',
            'message 2': 'sending a special treat your way'
        })

    # Change this variable to desired value - when wallet value drops below this, no more trades will be executed
    MIN_BALANCE = 500

    wallet_balance = getWalletValue()

    if wallet_balance < MIN_BALANCE:
        return json.dumps({
            'code': 'stopped',
            'message': 'wallet balance is less than the minimum required balance'
        })

    tradeType = webhook_message['TradeType']
    orderType = webhook_message['OrderType']
    entryPrice = float(webhook_message['EntryPrice'])
    orderSymbol = webhook_message['OrderSymbol'] + 'USDT'
    stopLossPct = float(webhook_message['StopLoss']) + 0.5 # 0.5 is added to account for fees so that the liquidation price is our stop loss
    takeProfit = float(webhook_message['TakeProfit'])

    side = "Buy" if "B" in orderType else "Sell"

    # Make sure any strategies you add, you also must add them to this map here
    trade_classes = {
        "SWING": BybitSwing,
        "SCALP": BybitScalp,
        "SCALE": BybitScale,
        "BBMA": Binance.BBMA,
        "GRID": Binance.SCALE,
        "WRSI": Binance.WRSI,
        "MRSI": Binance.MRSI
    }

    trade_class = trade_classes.get(tradeType)
    if trade_class:
        # specific to the bybit exchange
        if tradeType in ["SWING", "SCALP", "SCALE"]: 
            totalMargin = getTotalMargin()
            MAX_RISK = 500 # ensures our max amount of total margin for our active positions doesn't exceed this value. No new trades are taken beyond this value
            print('Total Margin:', totalMargin)
            if totalMargin >= MAX_RISK:
                return json.dumps({
                    'code': 'stopped',
                    'message': 'position size extended max allocated risk'
                })
            else: 
                trade = trade_class()
                trade.execute_trade(orderType, entryPrice, stopLossPct, takeProfit, orderSymbol, side)
        else:
            trade = trade_class()
            trade.execute_trade(orderType, entryPrice, stopLossPct, takeProfit, orderSymbol, side)
    else:
        print('Error! TradeType not Found!')

    return json.dumps({
        'code': 'success',
        'message': 'webhook received and processed'
    })


# Creating the parent class for the Bybit Exchange
class BybitExchange:
    '''
    This will be our Trading Account
    '''
    def __init__(self, endpoint, api_key, api_secret, ORDER_SIZE):
        self.session_auth = usdt_perpetual.HTTP(
            endpoint=endpoint,
            api_key=credentials.BB_KEY,
            api_secret=credentials.BB_SECRET
        )
        self.ORDER_SIZES = ORDER_SIZE
    
    # This function will set the leverage to the max value depending on our stop loss - this allows us to take more trades at a time
    # Understand the purpose of this strategy before using it - a 2% stop loss is 50x leverage!!! Be careful!!!
    # The max you lose is your ordersize, so set the ordersize variable later in the script to modify your risk.
    def set_leverage(self, symbol, stopLossPct):
        self.leverage = round(100 / stopLossPct, 2)
        
        # Differnt coins on crypto will have different max leverage values e.g. 25x, therefore can't set leverage to 100 or 50 in this case.
        positionDetails = self.session_auth.my_position(symbol=symbol)
        positionInfo = (positionDetails['result'])[0]['leverage']
        if positionInfo != self.leverage:
            try:
                self.session_auth.set_leverage(symbol=symbol, buy_leverage=self.leverage, sell_leverage=self.leverage)
            except:
                try:
                    self.leverage = 50
                    self.session_auth.set_leverage(symbol=symbol, buy_leverage=self.leverage, sell_leverage=self.leverage)
                except:
                    try:
                        self.leverage = 25
                        self.session_auth.set_leverage(symbol=symbol, buy_leverage=self.leverage, sell_leverage=self.leverage)
                    except:
                        print('Unable to Set Leverage')
        print(
                '------------------------------------------------------------------------', '\n',
                'Leverage Set to: ', str(self.leverage) + 'x')

    # EXECUTE THE TRADE
    def execute_trade(self, orderType, entryPrice, stopLoss, takeProfit, orderSymbol, side):
        self.set_leverage(orderSymbol, stopLoss)

        time.sleep(0.1)

        orderSize = self.ORDER_SIZES.get(orderType, 50)
        orderQty = round(((orderSize * self.leverage) / (entryPrice)), 3)
        
        # Executing the trade based on order details in the webhook
        self.session_auth.place_active_order(
            symbol=orderSymbol,
            side=side,
            order_type="Market",
            qty=orderQty,
            take_profit_price=takeProfit,
            stop_loss_price=stopLoss,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False
        )
        # Print statement to confirm trade has been taken
        print(
            '------------------------------------------------------------------------', '\n'
            'Order to', side, str(orderQty), 'of', orderSymbol, 'at', entryPrice, 'exectued.', '\n'
            '------------------------------------------------------------------------', '\n'
            'Order Size:', orderSize, ' | ', 'Leverage:', self.leverage,
            '------------------------------------------------------------------------', '\n'
        )

# Inherit the Bybit Exchange
# Modify these classes to fit your strategy but this is an example of how I have done it
class BybitSwing(BybitExchange):
    '''
    This is the Bybit SWING Trading Account -> Executing HTF Manual Alert Trades with Larger Order Sizes and Trade Durations as well as HTF Algotrading
    '''
    def __init__(self):
        endpoint="https://api.bybit.com"
        api_key=credentials.BB_KEY
        api_secret=credentials.BB_SECRET
        
        # Vary the ordersize for each acount depending on risk tolerance. As this is higher time frame, higher ordersize is preferred personally.
        ORDER_SIZE = {
            'B1': 100,
            'S1': 100,
        }
        super().__init__(endpoint, api_key, api_secret, ORDER_SIZE)

class BybitScalp(BybitExchange):
    '''
    This is the Bybit SCALP Account - STF Manual Alert Trades with Smaller Order Sizing and Shorter Trade Duration
    '''
    def __init__(self):
        endpoint="https://api.bybit.com"
        api_key=credentials.BB_KEY
        api_secret=credentials.BB_SECRET
        
        # as this is lower time frame, smaller order sizes are preferred as higher risk
        ORDER_SIZE = {
            'B1': 50,
            'S1': 50,
        }
        super().__init__(endpoint, api_key, api_secret, ORDER_SIZE)

# As well as adding other accounts to the same exchange, we can also add different strategies to the same exchange
# This is the scale strategy, where we are scaling into a short with limit orders ranging from entry price to stop loss
class BybitScale(BybitExchange):
    '''
    Bybit SCALE Strategy - 
    '''
    def __init__(self):
        endpoint="https://api.bybit.com"
        api_key=credentials.BB_KEY
        api_secret=credentials.BB_SECRET
        # This is the ordersize of the whole order (sum of all the limit order sizes)
        # The number after S will indicate how many grids we would like e.g. S5 = 5 grids = 5 limit orders
        ORDER_SIZES = {
            'S1': 50,
            'S2': 100,
            'S3': 150,
            'S5': 250,
            'S7': 350
        }
        super().__init__(endpoint, api_key, api_secret, ORDER_SIZES)

    def execute_trade(self, orderType, entryPrice, stopLoss, takeProfit, orderSymbol, side):
        self.set_leverage(orderSymbol, stopLoss)

        time.sleep(0.1) 

        orderSize = self.ORDER_SIZES.get(orderType, 50)

        # Trading logic behind the limit order grid which ranges from entry price to stop loss
        GRIDS = int(orderType[1:])
        stopLossPrice = entryPrice * (1 - stopLoss/100) # Get the SL in price
        gridSize = (entryPrice - stopLossPrice) / GRIDS # Calculate size of grid
        orderSizePerGrid = (orderSize / GRIDS) # get the ordersize per grid e.g. 100 ordersize with S5 will have 5 limit orders with each ordersize of 20

        if orderSizePerGrid < 15: # This is below the Bybit minimum ordersize value so will give an error
            raise Exception("ORDERSIZE is too small! Please increase ORDERSIZE") 
        
        # Executing our limit orders per grid in the gridbox
        for i in range(GRIDS):
            quantity = round((orderSizePerGrid / (entryPrice - i * gridSize))*10, 4)
            price = round(entryPrice + i * gridSize, 2)
            print(price)
            print(quantity)
            self.session_auth.place_active_order(
                symbol=orderSymbol,
                side=side,
                order_type="Limit",
                qty=quantity,
                price=price,
                time_in_force="GoodTillCancel",
                reduce_only=False,
                close_on_trigger=False,
                stop_loss_price=stopLossPrice
            )

            # Print Statement to confirm our grid
            print(
                '------------------------------------------------------------------------', '\n'
                'Order to', side, str(quantity), 'of', orderSymbol, 'at', price, 'exectued.', '\n'
                '------------------------------------------------------------------------', '\n'
                'Order Size:', orderSize, ' | ', 'Leverage:', self.leverage,
                '------------------------------------------------------------------------', '\n'
            )

# This is how we would introduce a new crypto exchange with different API and different strategies
# This is not limited to crypto, it can also be applied to FX, Stocks, Commodities etc. as these are all displayed on trading view, hence will output alerts
class Binance:
    """
    This is the Binance SPOT Account - Using HTF Indicators and Strategies to execute buys for the long term spot account
    """  
    # Here we are running different strategies to buy and hold long term rather than using standard DCA
    # This strategies are fully automated and don't require manual setting of alerts in TradingView
    # The pinescript code for BBMA is displayed in the Pinescript file

    # This strategy uses the Weekly Bollinger Bands and 200 Moving Average to buy different assets on Binance.
    class BBMA:

        def __init__(self, tradeType):
            self.client = Client(api_key=credentials.BNC_KEY, api_secret=credentials.BNC_SECRET)
            self.tradeType = tradeType

        def execute_trade(self, orderType, entryPrice, stopLossPct, takeProfit, orderSymbol, side):
            # If we have a specific asset that we just want to track and not buy then we can do the following
            # Here i am using SP500 and Nasdaq futures to issue signals, which I will decide if I want to manually spot buy BTC 
            # This is just an example of how you can run a pinescript indicator on an asset and use it to issue signals rather than execute trades
            if orderSymbol in ['ES1', 'NQ1']:
                print(f"Buy Signal on {orderSymbol}")
                return
            
            # Again we specify the ordersize for each alert that is triggered. 
            ORDERSIZE = 25
            quantity = round((ORDERSIZE / entryPrice), 4)
            
            side = "BUY" if "B" in orderType else "SELL"

            order = self.client.create_order(
                symbol=orderSymbol.strip(),
                side=side,
                type='MARKET',
                quantity=quantity
            )

            print(
                '------------------------------------------------------------------------', '\n'
                'Order to', side, str(quantity), 'of', orderSymbol, 'has been processed.', '\n'
                '------------------------------------------------------------------------', '\n'
            )
            
            # In the Bybit Account we were querying the api to get the active positions, and we can also get our transaction history with our getTransactions function is functions.py
            # Here we are loggign our spot buys into a CSV file.
            # This is again just for example to show we can do either. We can also query Binance and do the same but since we aren't taking many orders, this is preferred in this scenario
            self.write_trade_to_csv(ORDERSIZE, self.tradeType, orderType, entryPrice, orderSymbol, side)

        def write_trade_to_csv(self, ORDERSIZE, tradeType, orderType, entryPrice, orderSymbol, side):
            now = datetime.datetime.now()
            time = now.strftime("%d/%m/%Y")
            trade_data = [time, tradeType, orderSymbol, side, entryPrice, ORDERSIZE]
            with open('trades.csv', 'a') as file:
                writer = csv.writer(file)
                writer.writerow(trade_data)

    # In Bybit I displayed the scale function for scaling into a short
    # This can also be done the other way round and be used to scale into a long / spot buy an asset over a range.
    class SCALE:
        def __init__(self):
            self.client = Client(api_key=credentials.BNC_KEY, api_secret=credentials.BNC_SECRET)

        def execute_trade(self, orderType, entryPrice, stopLossPct, takeProfit, orderSymbol, side):
            
            ORDERSIZE = 95
            GRIDS = 4

            symbol = orderSymbol
            stopLossPrice = entryPrice * (1 - stopLossPct/100)
            gridSize = (entryPrice - stopLossPrice) / GRIDS
            
            orderSizePerGrid = (ORDERSIZE / GRIDS) / (entryPrice - i * gridSize)
            
            if orderSizePerGrid < 20:
                raise Exception("ORDERSIZE is too small! Please increase ORDERSIZE")
            
            for i in range(GRIDS):
                quantity = round(((ORDERSIZE / GRIDS) / (entryPrice - i * gridSize)), 4)
                price = round(entryPrice - i * gridSize, 2)

                print(f'Price for Grid {i+1}: {price}')

                if i == 0:
                    order = self.client.create_order(
                        symbol=symbol,
                        side="BUY",
                        type='MARKET',
                        quantity=quantity,
                    )
                    time.sleep(0.5)

                else:
                    order = self.client.create_order(
                        symbol=symbol,
                        side="BUY",
                        type='LIMIT',
                        timeInForce='GTC',
                        quantity=quantity,
                        price=price
                    )
                print(f'Grid {i+1} Executed at price: {price}!')
                time.sleep(0.5)

    # Example of adding another strategy
    class WRSI:

        def __init__(self, tradeType):
            self.client = Client(api_key=credentials.BNC_KEY, api_secret=credentials.BNC_SECRET)
            self.tradeType = tradeType

        def execute_trade(self, orderType, entryPrice, stopLossPct, takeProfit, orderSymbol, side):
            ...
      
    # In BBMA I metioned how we can run a strategy and issue a signal or execute trades with the same strategy.
    # If the strategy is just a signal, then we can just turn this into a separate class as below
    class MRSI:
        """
        Sell Signal for Trades and Spot Wallet
        """
        def __init__(self, orderSymbol):
            self.orderSymbol = orderSymbol

            print(f"Sell Signal for {orderSymbol.strip()} has been issued! Market is Overbought, Consider Selling!")
        
        def execute_trade(self, orderType, entryPrice, stopLossPct, takeProfit, orderSymbol, side):
            pass

if __name__ == '__main__':
    app.run(debug=True)
 