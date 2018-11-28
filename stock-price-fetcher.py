#!/usr/bin/env python
import os
import time
import threading
import MySQLdb

from yahoofinancials import YahooFinancials
# Database connection
SQL_HOST = '35.231.26.118'
SQL_USER = 'petroleum'
SQL_PSWD = 'petroleum'
SQL_DB = 'stockdata'

# File locations
DIRNAME = os.path.dirname(__file__)
STOCK_FILES = [ DIRNAME + '/conf/hel.stx' ]
INDICES_FILE = DIRNAME + '/conf/indices.stx'
SCRIPT_LOG_FILE = DIRNAME + '/log/script.log'
SQL_LOG_FILE = DIRNAME + '/log/sql.log'

# Log severitys
LOG_SEVERITY_INFO = 'INFORMATION'
LOG_SEVERITY_WARNING = 'WARNING'
LOG_SEVERITY_ERROR = 'ERROR'

# Threading
STOCK_INFO_FETCHER_THREADS = 12

#Timezone offset
os.environ['TZ'] = 'Europe/Helsinki'
time.tzset()

# Script functions and classes declaration
def log(log_file, severity, message):
	with open(log_file, 'a') as log:
		log.write(time.asctime(time.localtime(time.time())))
		log.write('\t')
		log.write('[' + severity + ']')
		log.write('\t')
		log.write(message)
		log.write('\n')

def connect_to_database(thread_id):
	db = MySQLdb.connect(host=SQL_HOST, user=SQL_USER, passwd=SQL_PSWD, db=SQL_DB)
	log(SCRIPT_LOG_FILE, LOG_SEVERITY_INFO, 'Thread: ' + thread_id + ', connected to database: ' + SQL_DB + ', on host: ' + SQL_HOST + str(db))
	return db

def close_connection_to_database(thread_id, db):
	db.close()
	log(SCRIPT_LOG_FILE, LOG_SEVERITY_INFO, 'Thread: ' + thread_id + ', closed connection to database: ' + SQL_DB + ', on host: ' + SQL_HOST)

def get_timestamp_for_db():
	now = time.localtime(time.time())
	return str(time.strftime("%Y-%m-%d %H:%M:%S", now))

def get_timestamp_for_db_query():
	now = time.localtime(time.time())
	return str(time.strftime("%Y-%m-%d", now)) + '%'

def create_query(query, arguments):
	return query.format(*arguments)

def execute_sql_with_logging(cursor, sql):
	log(SQL_LOG_FILE, LOG_SEVERITY_INFO, 'Executing sql: ' + sql)
	return cursor.execute(sql)

def store_stock_info(db, stock, stock_info):
	cursor = db.cursor()

	sql = "SELECT * FROM markets WHERE market = '{}'".format(stock_info.get_stock_exchange())
	number_of_markets = execute_sql_with_logging(cursor,sql) # Maximum one result row due to PK constraint in markets table
	if (number_of_markets == 0):
		sql = "INSERT INTO markets VALUES('{}')".format(stock_info.get_stock_exchange())
		execute_sql_with_logging(cursor, sql)
		db.commit()

    	sql = "SELECT * FROM stocks WHERE ticker = '{}'".format(stock)
	number_of_stocks = execute_sql_with_logging(cursor, sql)
	if (number_of_stocks == 0):
		sql = "INSERT INTO stocks VALUES('{}', '{}', '{}')".format(stock, stock_info.get_stock_exchange(), stock_info.get_market_cap())
		execute_sql_with_logging(cursor, sql)
		db.commit()
	else: # Maximum one result row due to PK constraing in stocks table
		sql = "UPDATE stocks SET market = '{}', marketcap = '{}' WHERE ticker = '{}'".format(stock_info.get_stock_exchange(), stock_info.get_market_cap(), stock)
		execute_sql_with_logging(cursor, sql)
		db.commit()

	sql = "SELECT * FROM stocks s JOIN prices p ON s.ticker = p.ticker WHERE s.ticker = '{}' AND p.date LIKE '{}'".format(stock, get_timestamp_for_db_query())
	number_of_prices = execute_sql_with_logging(cursor, sql)
	if (number_of_prices == 0): # Doesn't exist any prices, insert fresh ones
		sql = "INSERT INTO prices (ticker, date, previousclose, open, daytrend) VALUES('{}', '{}', {}, {}, '{}')" \
		.format(stock, get_timestamp_for_db(), stock_info.get_prev_close_price(), stock_info.get_open_price(), stock_info.get_current_price())
		execute_sql_with_logging(cursor, sql)
		db.commit()
	elif (number_of_prices == 1): # Update prices
		stock_and_prices_result = cursor.fetchall()
		stock_and_prices = stock_and_prices_result[0] # Should be exactly one!
		daytrend =  str(stock_and_prices[9]) + ';{}'.format(stock_info.get_current_price())
		sql = "UPDATE prices SET date = '{}', previousclose = {}, open = {}, daytrend = '{}' WHERE id = {}"	\
		.format(get_timestamp_for_db(), stock_info.get_prev_close_price(), stock_info.get_open_price(), daytrend, stock_and_prices[3])
		execute_sql_with_logging(cursor, sql)
		db.commit()
	else: # This is wrong, we should only have exactly one result row
		log(SQL_LOG_FILE, LOG_SEVERITY_ERROR, 'There exists more than one price-row for ticker: ' + stock + ' and date: ' + get_timestamp_for_db)

def store_index_info(db, index, index_info):
	cursor = db.cursor()

	sql = "SELECT * FROM markets WHERE market = '{}'".format(index_info.get_stock_exchange())
        number_of_markets = execute_sql_with_logging(cursor,sql) # Maximum one result row due to PK constraint in markets table
        if (number_of_markets == 0):
                sql = "INSERT INTO markets VALUES('{}')".format(index_info.get_stock_exchange())
                execute_sql_with_logging(cursor, sql)
                db.commit()
	
        sql = "SELECT * FROM indices i WHERE i.index = '{}'".format(index)
        number_of_indices = execute_sql_with_logging(cursor, sql)
        if (number_of_indices == 0):
                sql = "INSERT INTO indices VALUES('{}', '{}')".format(index, index_info.get_stock_exchange())
                execute_sql_with_logging(cursor, sql)
                db.commit()
        else: # Maximum one result row due to PK constraing in index table
                sql = "UPDATE indices i SET market = '{}' WHERE i.index = '{}'".format(index_info.get_stock_exchange(), index)
                execute_sql_with_logging(cursor, sql)
                db.commit()

        sql = "SELECT * FROM indices i JOIN prices p ON i.index = p.index WHERE i.index = '{}' AND p.date LIKE '{}'".format(index, get_timestamp_for_db_query())
        number_of_prices = execute_sql_with_logging(cursor, sql)
        if (number_of_prices == 0): # Doesn't exist any prices, insert fresh ones
		sql = "INSERT INTO prices (`index`, date, previousclose, open, daytrend) VALUES('{}', '{}', {}, {}, '{}')" \
                .format(index, get_timestamp_for_db(), index_info.get_prev_close_price(), index_info.get_open_price(), index_info.get_current_price())
                execute_sql_with_logging(cursor, sql)
                db.commit()
        elif (number_of_prices == 1): # Update prices
                index_and_prices_result = cursor.fetchall()
                index_and_prices = index_and_prices_result[0] # Should be exactly one!
                daytrend =  str(index_and_prices[8]) + ';{}'.format(index_info.get_current_price())
                sql = "UPDATE prices p  SET p.date = '{}', p.previousclose = {}, p.open = {}, p.daytrend = '{}' WHERE id = {}"     \
                .format(get_timestamp_for_db(), index_info.get_prev_close_price(), index_info.get_open_price(), daytrend, index_and_prices[2])
                execute_sql_with_logging(cursor, sql)
                db.commit()
        else: # This is wrong, we should only have exactly one result row
                log(SQL_LOG_FILE, LOG_SEVERITY_ERROR, 'There exists more than one price-row for index: ' + index + ' and date: ' + get_timestamp_for_db)

def fetch_and_store_stock_info(thread_id, db, stocks):
	for stock in stocks:
		log(SCRIPT_LOG_FILE, LOG_SEVERITY_INFO, 'Thread ' + thread_id + ' fetching stock info for ticker: ' + stock)
		stock_info = YahooFinancials(stock)
		stock_exchange = stock_info.get_stock_exchange()
		if (stock_exchange == 'none') or (stock_exchange == 'None') or (stock_exchange == 'NONE'):
			log(SCRIPT_LOG_FILE, LOG_SEVERITY_ERROR, 'Unable to store stock information for ticker: ' + stock + ', missing stock exchange')
		else:
			store_stock_info(db, stock, stock_info)

def fetch_and_store_index_info(thread_id, db, indices):
	for index in indices:
		log(SCRIPT_LOG_FILE, LOG_SEVERITY_INFO, 'Thread ' + thread_id + ' fetching info for index: ' + index)
		index_info = YahooFinancials(index)
		stock_exchange = index_info.get_stock_exchange()
                if (stock_exchange == 'none') or (stock_exchange == 'None') or (stock_exchange == 'NONE'):
                        log(SCRIPT_LOG_FILE, LOG_SEVERITY_ERROR, 'Unable to store index information for: ' + stock + ', missing stock exchange')
                else:
			store_index_info(db, index, index_info)

def start_stock_info_fetching(thread_id, stocks):
	log(SCRIPT_LOG_FILE, LOG_SEVERITY_INFO, 'Starting thread-id: ' + thread_id)
	db = connect_to_database(thread_id)
	fetch_and_store_stock_info(thread_id, db, stocks)
	close_connection_to_database(thread_id, db)
	log(SCRIPT_LOG_FILE, LOG_SEVERITY_INFO, 'Exiting thread-id: ' + thread_id)

def start_index_info_fetching(thread_id, indices):
	log(SCRIPT_LOG_FILE, LOG_SEVERITY_INFO, 'Starting thread-id: ' + thread_id)
	db = connect_to_database(thread_id)
	fetch_and_store_index_info(thread_id, db, indices)
	close_connection_to_database(thread_id, db)
	log(SCRIPT_LOG_FILE, LOG_SEVERITY_INFO, 'Exiting thread-id: ' + thread_id)

class StockFetcherThread(threading.Thread):
	def __init__(self, thread_id, stocks):
		threading.Thread.__init__(self)
		self.thread_id = thread_id
		self.stocks = stocks
	def run(self):
		start_stock_info_fetching(self.thread_id, self.stocks)

# Main script
for stock_file in STOCK_FILES:
	with open(stock_file, 'r') as current_stock_file:
		stocks = []
		for line in current_stock_file:
			stocks.append(line.strip('\n'))

with open(INDICES_FILE, 'r') as indices_file:
	indices = []
	for line in indices_file:
		indices.append(line.strip('\n'))

start_index_info_fetching('main', indices)

number_of_stocks = len(stocks)
thread_working_size = number_of_stocks//STOCK_INFO_FETCHER_THREADS
if (thread_working_size >= 2):
	thread_count = 0
	while thread_count < STOCK_INFO_FETCHER_THREADS:
		thread_stocks = ['']
		if ((thread_working_size * (thread_count + 1) + thread_working_size) <= number_of_stocks):
			thread_stocks = stocks[ thread_working_size * thread_count : thread_working_size *(thread_count + 1) ]
		else:
			thread_stocks = stocks[ thread_working_size * thread_count : number_of_stocks ]

		thread = StockFetcherThread('t' + str(thread_count), thread_stocks)
		thread.start()

		thread_count = thread_count + 1
else:
	start_stock_info_fetching('main', stocks)


