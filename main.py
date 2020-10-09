import os

from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *

import numpy as np
import pandas as pd
import talib



def process_all_tickers(msg):
    if isinstance(msg,list):
        update_df = pd.DataFrame(msg)
        tickers_df.update(update_df)


if __name__ == "__main__":  
    api_key = os.environ.get('binance_api')
    api_secret = os.environ.get('binance_api_secret')

    client = Client(api_key, api_secret)

    # setup
    tickers_data = client.get_ticker()
    tickers_df = pd.DataFrame(tickers_data)

    bsm = BinanceSocketManager(client)
    conn_key = bsm.start_ticker_socket(process_all_tickers)
    bsm.start()

