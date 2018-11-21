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
STOCK_FILES = [ '/usr/local/bin/get-rich-bitch/conf/hel-slim.stx' ]
LOG_FILE = '/usr/local/bin/get-rich-bitch/log/stock-debug.log'

# Threading
STOCK_INFO_FETCHER_THREADS = 5

#Timezone offset
os.environ['TZ'] = 'Europe/Helsinki'
time.tzset()

# Script functions and classes declaration
def connect_to_database(thread_id):
	db = MySQLdb.connect(host=SQL_HOST,
        		user=SQL_USER,
                passwd=SQL_PSWD,
                db=SQL_DB)
	print 'Thread \"' + thread_id + '\" connected to database ' + SQL_DB + ' on host ' + SQL_HOST + str(db)
	return db

def close_connection_to_database(thread_id, db):
	db.close()
	print 'Thread \"' + thread_id + '\" closed connection to database ' + SQL_DB + ' on host ' + SQL_HOST

def get_timestamp_for_db():
	now = time.localtime(time.time())
	return str(time.strftime("%Y-%m-%d %H:%M:%S", now))

def get_timestamp_for_db_query():
	now = time.localtime(time.time())
	return str(time.strftime("%Y-%m-%d", now)) + '%'

def log_stock_info(stock, stock_info):
    currency = stock_info.get_currency()
    # Just log for now..
    with open(LOG_FILE, 'a') as log:
		log.write(time.asctime(time.localtime(time.time())))
        	log.write('\t')
        	log.write(str(stock_info.get_stock_exchange()))
		log.write('\t')
		log.write(stock)
	        log.write('\t')
	        log.write(str(stock_info.get_market_cap()))
	        log.write('\t')
	        log.write(str(stock_info.get_prev_close_price()) + currency)
	        log.write('\t')
	        log.write(str(stock_info.get_open_price()) + currency)
	        log.write('\t')
	        log.write(str(stock_info.get_current_price()) + currency)
	        log.write('\t')
	        log.write(str(round(stock_info.get_current_change())) + currency)
	        log.write('(' + str(round(stock_info.get_current_percent_change()*100, 2)) + '%)\n')

def store_stock_info(db, stock, stock_info):
	cursor = db.cursor()
	sql = "select * from markets where market = '%s'" % stock_info.get_stock_exchange()

	number_of_markets = cursor.execute(sql)
	if (number_of_markets == 0):
		sql = "insert into markets values('%s')" % (stock_info.get_stock_exchange())
                cursor.execute(sql) 
		db.commit()

        sql = "select * from stocks where ticker = '%s'" % stock
	number_of_stocks = cursor.execute(sql)
	if (number_of_stocks == 0):
		sql = "insert into stocks values('%s', '%s', '%s')" % (stock, stock_info.get_stock_exchange(), stock_info.get_market_cap())
                cursor.execute(sql)
                db.commit()
	else:
		sql = "update stocks set marketcap = '%s'" % stock_info.get_market_cap()
		cursor.execute(sql)
		db.commit()

	sql = "select * from stocks s join prices p on s.ticker = p.ticker where s.ticker = '%s' and p.date like '%s'" % \
		(stock, get_timestamp_for_db_query())

	print sql
	number_of_prices = cursor.execute(sql)
	if (number_of_prices == 0): # Doesn't exist any prices, insert fresh ones
		sql = "insert into prices (ticker, date, previousclose, open, daytrend) values('%s', '%s', '%d', '%d', '%s')" % \
			 (stock, get_timestamp_for_db(), stock_info.get_prev_close_price(), stock_info.get_open_price(), stock_info.get_current_price())
		cursor.execute(sql)
		db.commit()
	else:
		result = cursor.fetchall()
		for row in result:
			print(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])

def fetch_and_store_stock_info(thread_id, db, stocks):
	for stock in stocks:
		print 'Thread \"' + thread_id + '\" fetching stock info for ticker -> ' + stock
		stock_info = YahooFinancials(stock)
		log_stock_info(stock, stock_info)
		store_stock_info(db, stock, stock_info)

class StockFetcherThread (threading.Thread):
	def __init__(self, thread_id, stocks):
		threading.Thread.__init__(self)
		self.thread_id = thread_id
		self.stocks = stocks
	def run(self):
		print 'Starting thread-id: ' + self.thread_id
		db = connect_to_database(self.thread_id)
		fetch_and_store_stock_info(self.thread_id, db, self.stocks)
		close_connection_to_database(self.thread_id, db)
		print 'Exiting thread-id:' + self.thread_id

# Main script
for stock_file in STOCK_FILES:
	with open(stock_file, 'r') as current_stock_file:
		stocks = []
		for line in current_stock_file:
			stocks.append(line.strip('\n'))

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
	fetch_and_log_stocks('main', stocks)
