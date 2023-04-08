import hashlib
import hmac
import json
import time

import requests
from binance.enums import ORDER_TYPE_MARKET

import config


class TradeEngine:
    def __init__(self, client):
        self.client = client

    def get_client(self):
        return self.client

    def place_order(self, side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
        try:
            print(f"sending order {order_type} - {side} {quantity} {symbol}")
            order = self.client.create_order(symbol=symbol,
                                             side=side,
                                             type=order_type,
                                             quantity=quantity)
        except Exception as e:
            print("an exception occured - {}".format(e))
            return False

        return order

    # Function to place order on Binance Futures Testnet API with TP and SL
    def place_order_optimized(self, symbol, side, quantity, price, tp, sl):
        timestamp = int(time.time() * 1000)
        params = {
            'symbol': symbol,
            'side': side,
            'type': 'LIMIT',
            'timeInForce': 'GTC',
            'quantity': quantity,
            'price': price,
            'stopPrice': sl,
            'timestamp': timestamp,
            'recvWindow': 5000,
            'newClientOrderId': f'{symbol}-{timestamp}'
        }
        if tp is not None:
            params['type'] = 'TAKE_PROFIT_LIMIT'
            params['stopPrice'] = tp
            params['timeInForce'] = 'GTX'
        endpoint = '/fapi/v1/order/test'
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(config.API_KEY, query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        headers = {'X-MBX-APIKEY': config.API_KEY}
        params['signature'] = signature
        response = requests.post(f'https://testnet.binancefuture.com{endpoint}', headers=headers, params=params)
        return json.loads(response.content)
