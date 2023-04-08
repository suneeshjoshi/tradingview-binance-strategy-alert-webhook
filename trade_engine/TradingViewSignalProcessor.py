import hashlib
import hmac
import json
import logging

from flask import request

import config
from config import RESPONSE, MESSAGE, STATUS, SUCCESS, FAIL
from trade_engine.TradeEngine import TradeEngine


class TradingViewSignalProcessor:
    def __init__(self, client, input_request):
        self.request = input_request
        self.client = client
        self.trading_engine = TradeEngine(client)

    def process_signal(self):
        # print(request.data)
        data = json.loads(request.data)

        if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
            return self.get_response(FAIL, "Error! Invalid passphrase")

        side = data['strategy']['order_action'].upper()
        quantity = data['strategy']['order_contracts']

        order_response = self.trading_engine.place_order(side, quantity, data['ticker'])
        logging.info(order_response)

        if order_response:
            return self.get_response(SUCCESS, "Order Executed", order_response)
        else:
            print("Order Failed")
            return self.get_response(FAIL, "Error! Order Failed", order_response)

    # Function to verify Tradingview webhook
    def verify_webhook(self):
        signature = self.request.headers.get('X-Secret')
        payload = self.request.data.decode('utf-8')
        if signature == hmac.new(config.WEBHOOK_PASSPHRASE.encode('utf-8'), payload.encode('utf-8'),
                                 hashlib.sha256).hexdigest():
            return True
        else:
            return False

    def process_signal_optimized(self):
        if self.verify_webhook():
            data = request.get_json()
            symbol = data['symbol']
            side = data['side']
            quantity = data['quantity']
            price = data['price']
            tp = data.get('tp', None)
            sl = data.get('sl', None)
            response = self.trading_engine.place_order_optimized(symbol, side, quantity, price, tp, sl)
            return self.get_response(SUCCESS, "Order Executed", response)
        else:
            return self.get_response(FAIL, "Error! Webhook verification failed")

    def get_response(status, message, order_response=""):
        return {
            STATUS: status,
            MESSAGE: message,
            RESPONSE: order_response
        }
