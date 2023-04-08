import logging

from binance.client import Client
from flask import Flask, render_template, request

import config
from trade_engine.TradingViewSignalProcessor import TradingViewSignalProcessor

app = Flask(__name__)
client = Client(config.API_KEY,
                config.API_SECRET,
                tld='com',
                testnet=True)


def main():
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logging.info('Started')

    app.run(debug=config.DEBUG_MODE)
    logging.info('Finished')


@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/version')
def get_version():
    return "1.0"


@app.route('/webhook', methods=['POST'])
def webhook():
    tvsp = TradingViewSignalProcessor(client, request)
    tvsp.process_signal()


if __name__ == '__main__':
    main()
