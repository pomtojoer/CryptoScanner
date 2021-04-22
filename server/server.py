# Binance modules
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import KLINE_INTERVAL_1MINUTE

import psycopg2

# ***********************************************************
# **********            Table descriptions          *********
# ***********************************************************

# active table constants
ACTIVE_TABLE_NAME = 'active_pairs'
ASSET_NAME = 'asset_name'
TRACKING_STATUS = 'tracking_status'
EXCHANGE_STATUS = 'exchange_status'
BASE_ASSET = 'base_asset'
BASE_ASSET_PRECISION = 'base_asset_precision'
QUOTE_ASSET = 'quote_asset'
QUOTE_ASSET_PRECISION = 'quote_asset_precision'
IS_SPOT_TRADING_ALLOWED = 'is_spot_trading_allowed'
IS_MARGIN_TRADING_ALLOWED = 'is_margin_trading_allowed'
LAST_UPDATE = 'last_update'

# tracking status options
TRACKING_STATUS_STOPPED = 'stopped'
TRACKING_STATUS_RUNNING = 'running'
TRACKING_STATUS_INITIALISING = 'initialising'

# pair table constants
OPEN_TIME = 'open_time'
CLOSE_TIME = 'close_time'
OPEN_PRICE = 'open_price'
HIGH_PRICE = 'high_price'
LOW_PRICE = 'low_price'
CLOSE_PRICE = 'close_price'
VOLUME = 'volume'
QUOTE_VOLUME = 'quote_volume'
NUMBER_OF_TRADES = 'number_of_trades'
TAKER_BUY_BASE_VOLUME = 'taker_buy_base_volume'
TAKER_BUY_QUOTE_VOLUME = 'taker_buy_quote_volume'


# **********************************************************
# **********             Pair data class           *********
# **********************************************************

class PairData:
    def __init__(self, pair, client, conn) -> None:
        # pair and client
        self.pair = ''
        self.client = None
        self.conn = None

        # initialising connections
        self.init_binance_connection(client)
        self.init_postgres_connection(conn)

        # initialising tables
        self.init_pair_info(pair)

        # candle data
        self.candle_times = []
        self.candle_opens = []
        self.candle_closes = []
        self.candle_highs = []
        self.candle_lows = []
        self.candle_volumes = []
        
        # indicator data
        self.indicators = []

    def init_binance_connection(self, client):
        if type(client) is not Client:
            raise ValueError('Invalid client type')

        system_status = client.get_system_status()
        if system_status['status'] == 1:
            raise ValueError(f'Connection error: {system_status["msg"]}')
        self.client = client

    def init_postgres_connection(self, conn):
        if type(conn) is not psycopg2.extensions.connection:
            raise ValueError('Invalid postgres connection type')
        
        self.conn = conn
    
    def init_pair_info(self, pair):
        pair_info = self.client.get_symbol_info(pair)
        if pair_info is None:
            raise ValueError('Invalid pair')
        
        self.pair = pair.upper()

        cur = self.conn.cursor()

        cur.execute(
            f'''INSERT INTO {ACTIVE_TABLE_NAME} (
                {ASSET_NAME},
                {TRACKING_STATUS},
                {EXCHANGE_STATUS}, 
                {BASE_ASSET},
                {BASE_ASSET_PRECISION},
                {QUOTE_ASSET},
                {QUOTE_ASSET_PRECISION},
                {IS_SPOT_TRADING_ALLOWED},
                {IS_MARGIN_TRADING_ALLOWED}
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ({ASSET_NAME}) DO UPDATE SET (
                {TRACKING_STATUS},
                {EXCHANGE_STATUS}, 
                {BASE_ASSET},
                {BASE_ASSET_PRECISION},
                {QUOTE_ASSET},
                {QUOTE_ASSET_PRECISION},
                {IS_SPOT_TRADING_ALLOWED},
                {IS_MARGIN_TRADING_ALLOWED}
            ) = (
                EXCLUDED.{TRACKING_STATUS},
                EXCLUDED.{EXCHANGE_STATUS}, 
                EXCLUDED.{BASE_ASSET},
                EXCLUDED.{BASE_ASSET_PRECISION},
                EXCLUDED.{QUOTE_ASSET},
                EXCLUDED.{QUOTE_ASSET_PRECISION},
                EXCLUDED.{IS_SPOT_TRADING_ALLOWED},
                EXCLUDED.{IS_MARGIN_TRADING_ALLOWED}
            );''', (
                self.pair,
                TRACKING_STATUS_STOPPED,
                pair_info['status'],
                pair_info['baseAsset'],
                pair_info['baseAssetPrecision'],
                pair_info['quoteAsset'],
                pair_info['quoteAssetPrecision'],
                pair_info['isSpotTradingAllowed'],
                pair_info['isMarginTradingAllowed']
            )
        )

        cur.execute(f'SELECT * FROM information_schema.tables WHERE table_name = \'{self.pair}\';')
        if cur.fetchone() is None:
            cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.pair} (
                {OPEN_TIME} BIGINT PRIMARY KEY,
                {CLOSE_TIME} BIGINT UNIQUE NOT NULL,
                {OPEN_PRICE} DOUBLE PRECISION NOT NULL,
                {HIGH_PRICE} DOUBLE PRECISION NOT NULL,
                {LOW_PRICE} DOUBLE PRECISION NOT NULL,
                {CLOSE_PRICE} DOUBLE PRECISION NOT NULL,
                {VOLUME} DOUBLE PRECISION NOT NULL,
                {QUOTE_VOLUME} DOUBLE PRECISION NOT NULL,
                {NUMBER_OF_TRADES} DOUBLE PRECISION NOT NULL,
                {TAKER_BUY_BASE_VOLUME} DOUBLE PRECISION NOT NULL,
                {TAKER_BUY_QUOTE_VOLUME} DOUBLE PRECISION NOT NULL
            );''')
        
        self.conn.commit()

    def start_tracking(self):
        self.update_tracking_status(TRACKING_STATUS_INITIALISING)

        self.bm = BinanceSocketManager(self.client)
        self.bm.daemon = False # change this
        self.conn_key = self.bm.start_kline_socket(self.pair, self.process_message, interval=KLINE_INTERVAL_1MINUTE)
        self.bm.start()
        self.init_pair_data()

        self.update_tracking_status(TRACKING_STATUS_RUNNING)

    def stop_tracking(self):
        self.bm.stop_socket(self.conn_key)
        self.update_tracking_status(TRACKING_STATUS_STOPPED)

    def update_tracking_status(self, status):
        cur = self.conn.cursor()
        cur.execute(f'UPDATE {ACTIVE_TABLE_NAME} SET {TRACKING_STATUS} = %s WHERE {ASSET_NAME} = %s', (status, self.pair))
        self.conn.commit()

    def process_message(self, msg):
        kline_data = msg['k']
        cur = self.conn.cursor()
        cur.execute(
            f'''INSERT INTO {self.pair} (
                {OPEN_TIME},
                {CLOSE_TIME},
                {OPEN_PRICE}, 
                {HIGH_PRICE},
                {LOW_PRICE},
                {CLOSE_PRICE},
                {VOLUME},
                {QUOTE_VOLUME},
                {NUMBER_OF_TRADES},
                {TAKER_BUY_BASE_VOLUME},
                {TAKER_BUY_QUOTE_VOLUME}
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ({OPEN_TIME}) DO UPDATE SET (
                {HIGH_PRICE},
                {LOW_PRICE},
                {CLOSE_PRICE},
                {VOLUME},
                {QUOTE_VOLUME},
                {NUMBER_OF_TRADES},
                {TAKER_BUY_BASE_VOLUME},
                {TAKER_BUY_QUOTE_VOLUME}
            ) = (
                EXCLUDED.{HIGH_PRICE},
                EXCLUDED.{LOW_PRICE},
                EXCLUDED.{CLOSE_PRICE},
                EXCLUDED.{VOLUME},
                EXCLUDED.{QUOTE_VOLUME},
                EXCLUDED.{NUMBER_OF_TRADES},
                EXCLUDED.{TAKER_BUY_BASE_VOLUME},
                EXCLUDED.{TAKER_BUY_QUOTE_VOLUME}
            );''', (
                kline_data.get('t', None),
                kline_data.get('T', None),
                kline_data.get('o', None),
                kline_data.get('h', None),
                kline_data.get('l', None),
                kline_data.get('c', None),
                kline_data.get('v', None),
                kline_data.get('q', None),
                kline_data.get('n', None),
                kline_data.get('V', None),
                kline_data.get('Q', None)
            )
        )
        self.conn.commit()

    def init_pair_data(self):
        # [
        #     [
        #         1499040000000,      // Open time
        #         "0.01634790",       // Open
        #         "0.80000000",       // High
        #         "0.01575800",       // Low
        #         "0.01577100",       // Close
        #         "148976.11427815",  // Volume
        #         1499644799999,      // Close time
        #         "2434.19055334",    // Quote asset volume
        #         308,                // Number of trades
        #         "1756.87402397",    // Taker buy base asset volume
        #         "28.46694368",      // Taker buy quote asset volume
        #         "17928899.62484339" // Ignore.
        #     ]
        # ]

        kline_data = (tuple(klines[0:-1]) for klines in self.client.get_historical_klines_generator(self.pair, KLINE_INTERVAL_1MINUTE, "2 day ago UTC"))
        query = f'''
            INSERT INTO {self.pair} (
                {OPEN_TIME},
                {OPEN_PRICE}, 
                {HIGH_PRICE},
                {LOW_PRICE},
                {CLOSE_PRICE},
                {VOLUME},
                {CLOSE_TIME},
                {QUOTE_VOLUME},
                {NUMBER_OF_TRADES},
                {TAKER_BUY_BASE_VOLUME},
                {TAKER_BUY_QUOTE_VOLUME}
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ({OPEN_TIME}) DO UPDATE SET (
                {HIGH_PRICE},
                {LOW_PRICE},
                {CLOSE_PRICE},
                {VOLUME},
                {QUOTE_VOLUME},
                {NUMBER_OF_TRADES},
                {TAKER_BUY_BASE_VOLUME},
                {TAKER_BUY_QUOTE_VOLUME}
            ) = (
                EXCLUDED.{HIGH_PRICE},
                EXCLUDED.{LOW_PRICE},
                EXCLUDED.{CLOSE_PRICE},
                EXCLUDED.{VOLUME},
                EXCLUDED.{QUOTE_VOLUME},
                EXCLUDED.{NUMBER_OF_TRADES},
                EXCLUDED.{TAKER_BUY_BASE_VOLUME},
                EXCLUDED.{TAKER_BUY_QUOTE_VOLUME}
            );'''
        cur = self.conn.cursor()
        cur.executemany(query, kline_data)
        self.conn.commit()

    

class PairManager:
    def __init__(self, api_key, api_secret, database='crypto-ta', user='postgres', password='postgres'):
        self.conn = psycopg2.connect(database=database, user=user, password=password)
        self.client = Client(api_key, api_secret)
        self.init_active_pair_table()

        self.pairs_data = {}

    def init_active_pair_table(self):
        cur = self.conn.cursor()
        cur.execute(f'SELECT * FROM information_schema.tables WHERE table_name = \'{ACTIVE_TABLE_NAME}\';')
        if cur.fetchone() is None:
            cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {ACTIVE_TABLE_NAME} (
                {ASSET_NAME} VARCHAR(20) PRIMARY KEY,
                {TRACKING_STATUS} VARCHAR(20) NOT NULL,
                {EXCHANGE_STATUS} VARCHAR(20) NOT NULL,
                {BASE_ASSET} VARCHAR(10) NOT NULL,
                {BASE_ASSET_PRECISION} SMALLINT NOT NULL,
                {QUOTE_ASSET} VARCHAR(10) NOT NULL,
                {QUOTE_ASSET_PRECISION} SMALLINT NOT NULL,
                {IS_SPOT_TRADING_ALLOWED} BOOLEAN NOT NULL,
                {IS_MARGIN_TRADING_ALLOWED} BOOLEAN NOT NULL,
                {LAST_UPDATE} BIGINT
            );''')

        info = self._client.get_exchange_info()

        print(info)


        self.conn.commit()

    def add_pair(self, pair):
        pair_data = PairData(pair, self.client, self.conn)
        self.pairs_data[pair] = pair_data

    def start_pair(self, pair):
        pair_data = self.pairs_data[pair]
        pair_data.start_tracking()

    def stop_pair(self, pair):
        pair_data = self.pairs_data[pair]
        pair_data.stop_tracking()

    def remove_pair(self, pair):
        pair_data = self.pairs_data[pair]
        #TODO: ADD REMOVE FROM TABLE

        self.pairs_data.pop(pair)


    
class BinanceSpotDataManager:
    def __init__(self) -> None:
        self.pairs = []

