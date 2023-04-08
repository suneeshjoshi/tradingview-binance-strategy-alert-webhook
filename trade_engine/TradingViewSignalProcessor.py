import json
import logging

from flask import request

import config
from trade_engine.TradeEngine import TradeEngine


class TradingViewSignalProcessor:
    def __int__(self, client, request):
        self.request = request
        self.client = client
        self.trading_engine = TradeEngine(self.client)

    def process_signal(self):
        # print(request.data)
        data = json.loads(request.data)

        if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
            return {
                "code": "error",
                "message": "Nice try, invalid passphrase"
            }

        side = data['strategy']['order_action'].upper()
        quantity = data['strategy']['order_contracts']

        order_response = self.trading_engine.place_order(side, quantity, data['ticker'])
        logging.info(order_response)

        if order_response:
            return {
                "code": "success",
                "message": "order executed"
            }
        else:
            print("order failed")

            return {
                "code": "error",
                "message": "order failed"
            }
