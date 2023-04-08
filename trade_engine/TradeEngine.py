from binance.enums import ORDER_TYPE_MARKET


class TradeEngine:
    def __int__(self, client):
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
