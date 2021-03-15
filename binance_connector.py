# Binance modules
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *

# Python processing modules
import sqlite3
import pandas as pd


class AllSymbolsTable:
    table_name = 'All_Symbols'
    symbol = 'symbol'
    status = 'status'
    base_assest = 'baseAsset'
    base_asset_precision = 'baseAssetPrecision'
    quoteAsset = 'quoteAsset'
    quotePrecision = 'quotePrecision'
    quoteAssetPrecision = 'quoteAssetPrecision'
    baseCommissionPrecision = 'baseCommissionPrecision'
    quoteCommissionPrecision = 'quoteCommissionPrecision'

class ActiveSymbolsTable:
    table_name = 'Active_Symbols'
    active_symbol = 'active_symbol'
    interval = 'interval'

class TickerKlineTable:
    open_time = 'open_time'
    open_price = 'open'
    high_price = 'high'
    low_price = 'low'
    close_price = 'close'
    vol = 'vol'
    close_time = 'close_time'
    quote_vol = 'quote_vol'
    no_of_trades = 'no_of_trades'
    taker_buy_base_vol = 'taker_buy_base_vol'
    taker_buy_quote_vol = 'taker_buy_quote_vol'

class DatabaseTables:
    db_filename = 'data.db'
    all_symbols = AllSymbolsTable.table_name
    active_symbols = ActiveSymbolsTable.table_name

class CustomBinanceSocketManager(BinanceSocketManager):

    def __init__(self, *args, **kwargs):
        super(CustomBinanceSocketManager, self).__init__(*args, **kwargs)
        self._db_filename = DatabaseTables.db_filename
        self._sql_conn = sqlite3.connect(self._db_filename, check_same_thread=False)
        self._initialise_all_tickers_table()
        self._initialise_active_tickers_table()

    def start_multiplex_kline_socket(self, tickers, interval):
        c = self._sql_conn.cursor()
        sql_command = f'SELECT {AllSymbolsTable.symbol} FROM {AllSymbolsTable.table_name} WHERE STATUS = \"TRADING\"'
        all_valid_symbols = [symbol[0] for symbol in c.execute(sql_command).fetchall()]
        valid_tickers = []
        for ticker in tickers:
            if ticker.upper() in all_valid_symbols:
                valid_tickers.append(ticker.lower())
            else:
                print(f'{ticker} is not a valid pair. This will be ignored.')

        streams = [f'{ticker}@kline_{interval}' for ticker in valid_tickers]
        multiplex_conn_key = super().start_multiplex_socket(streams, self._process_message)
        started_streams = [stream for stream in valid_tickers if stream in multiplex_conn_key]
        sql_command = f'''
            INSERT OR REPLACE INTO {ActiveSymbolsTable.table_name} (
                {ActiveSymbolsTable.active_symbol},
                {ActiveSymbolsTable.interval}
            ) VALUES (?, ?)
        '''
        c.executemany(sql_command, [(started_stream, interval) for started_stream in started_streams])
        self._sql_conn.commit()

        print('The following streams have been started: {} for {} interval'.format(', '.join(started_streams), interval))

        self._initialise_database(valid_tickers, interval)

        return multiplex_conn_key

    def _initialise_all_tickers_table(self):
        info = self._client.get_exchange_info()

        symbols_df = pd.DataFrame(info['symbols'])
        symbols_df = symbols_df[symbols_df.columns[:9]] 
        symbols_df.to_sql(name=AllSymbolsTable.table_name, con=self._sql_conn, if_exists='replace', index=False, index_label='symbol')

    def _initialise_active_tickers_table(self):
        sql_command = f'''
            CREATE TABLE IF NOT EXISTS {ActiveSymbolsTable.table_name} (
                {ActiveSymbolsTable.active_symbol}  TEXT PRIMARY KEY, 
                {ActiveSymbolsTable.interval}  TEXT,
                FOREIGN KEY({ActiveSymbolsTable.active_symbol}) REFERENCES {DatabaseTables.all_symbols}(symbol)
            );
        '''
        c = self._sql_conn.cursor()
        c.execute(sql_command)
        self._sql_conn.commit()

    def _initialise_database(self, tickers, interval):
        for ticker in tickers:
            # Initialising cursor
            c = self._sql_conn.cursor()

            table_name = f'{ticker}_{interval}'

            sql_command = f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {TickerKlineTable.open_time} INTEGER PRIMARY KEY,
                    {TickerKlineTable.open_price} DOUBLE,
                    {TickerKlineTable.high_price} DOUBLE,
                    {TickerKlineTable.low_price} DOUBLE,
                    {TickerKlineTable.close_price} DOUBLE,
                    {TickerKlineTable.vol} DOUBLE,
                    {TickerKlineTable.close_time} INTEGER,
                    {TickerKlineTable.quote_vol} DOUBLE,
                    {TickerKlineTable.no_of_trades} DOUBLE,
                    {TickerKlineTable.taker_buy_base_vol} DOUBLE,
                    {TickerKlineTable.taker_buy_quote_vol} DOUBLE
                );
            '''
            c.execute(sql_command)
            
            kline_data = [tuple(kline[:-1]) for kline in self._client.get_historical_klines(ticker.upper(), interval, "1 day ago UTC")]
            sql_command = f'''
                INSERT OR REPLACE INTO {table_name} (
                    {TickerKlineTable.open_time},
                    {TickerKlineTable.open_price},
                    {TickerKlineTable.high_price},
                    {TickerKlineTable.low_price},
                    {TickerKlineTable.close_price},
                    {TickerKlineTable.vol},
                    {TickerKlineTable.close_time},
                    {TickerKlineTable.quote_vol},
                    {TickerKlineTable.no_of_trades},
                    {TickerKlineTable.taker_buy_base_vol},
                    {TickerKlineTable.taker_buy_quote_vol}
                )
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            c.executemany(sql_command, kline_data)

            self._sql_conn.commit()

    def _process_message(self, msg):
        stream_data = msg['data']
        ticker = stream_data['s']
        ticker_data = stream_data['k']
        
        open_time = ticker_data['t']
        open_price = ticker_data['o']
        close_price = ticker_data['c']
        high_price = ticker_data['h']
        low_price = ticker_data['l']
        volume = ticker_data['v']
        close_time = ticker_data['T']
        quote_vol = ticker_data['q']
        no_of_trades = ticker_data['n']
        taker_buy_base_vol = ticker_data['V']
        taker_buy_quote_vol = ticker_data['Q']

        interval = ticker_data['i']

        table_name = f'{ticker}_{interval}'

        sql_command = f'''
            INSERT OR REPLACE INTO {table_name} (
                {TickerKlineTable.open_time},
                {TickerKlineTable.open_price},
                {TickerKlineTable.high_price},
                {TickerKlineTable.low_price},
                {TickerKlineTable.close_price},
                {TickerKlineTable.vol},
                {TickerKlineTable.close_time},
                {TickerKlineTable.quote_vol},
                {TickerKlineTable.no_of_trades},
                {TickerKlineTable.taker_buy_base_vol},
                {TickerKlineTable.taker_buy_quote_vol}
            )
            VALUES
                ({open_time}, {open_price}, {high_price}, {low_price}, {close_price}, {volume}, {close_time}, {quote_vol}, {no_of_trades}, {taker_buy_base_vol}, {taker_buy_quote_vol})
        '''

        c = self._sql_conn.cursor()
        c.execute(sql_command)
        self._sql_conn.commit()

