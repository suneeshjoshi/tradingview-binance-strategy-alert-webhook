import hashlib
import hmac
import json
import logging

from flask import request

import config
from config import RESPONSE, MESSAGE, STATUS, SUCCESS, FAIL
from trade_engine.TradeEngine import TradeEngine

STRATEGY = 'strategy'


class TradingViewSignalProcessor:
    def __init__(self, client, input_request):
        self.request = input_request
        self.client = client
        self.trading_engine = TradeEngine(client)

    def process_signal(self):
        # print(request.data)
        data = json.loads(request.data)

        verification_result = self.verify_webhook()
        if verification_result.get(STATUS) != SUCCESS:
            return verification_result

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
        data = json.loads(request.data)
        if config.ENABLE_TV_SIGNAL_SIGNATURE_CHECK:
            signature = self.request.headers.get('X-Secret')
            payload = data.decode('utf-8')
            if signature == hmac.new(config.WEBHOOK_PASSPHRASE.encode('utf-8'), payload.encode('utf-8'),
                                     hashlib.sha256).hexdigest():
                return self.get_response(SUCCESS, "Webhook Signature Verification Passed.")
            else:
                return self.get_response(FAIL, "Error! Webhook Signature Verification Failed.")
        else:
            if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
                return self.get_response(FAIL, "Error! Webhook Passphrase Verification Failed. Invalid passphrase")
            else:
                return self.get_response(SUCCESS, "Webhook Passphrase Verification Passed.")

    def process_signal_optimized(self):
        # Check if the verification passed or not
        verification_status = self.verify_webhook()
        if verification_status.get(STATUS) == SUCCESS:
            data = json.loads(request.data)
            strategy = data[STRATEGY]

            symbol = data['ticker']
            side = strategy['order_action'].upper()
            quantity = strategy['order_contracts']
            price = strategy['order_price']
            # Original, re-enable these once TP & SL values are received from tradingview
            # tp = data.get('tp', None)
            # sl = data.get('sl', None)

            tp = price + 10 if side == "BUY" else price - 10
            sl = price - 10 if side == "BUY" else price + 10

            response = self.trading_engine.place_order_optimized(symbol, side, quantity, price, tp, sl)
            return self.get_response(SUCCESS, "Order Executed", response)
        else:
            return verification_status

    def get_response(self, status, message, order_response=""):
        return {
            STATUS: status,
            MESSAGE: message,
            RESPONSE: order_response
        }
