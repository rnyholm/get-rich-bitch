#!/usr/bin/env python
import os
import threading
import logger as log
import dbhandler

from yahoofinancials import YahooFinancials

# File locations
DIRNAME = os.path.dirname(__file__)
STOCK_FILES = [ DIRNAME + '/conf/hel.stx' ]
INDICES_FILE = DIRNAME + '/conf/indices.stx'

# Threading
STOCK_INFO_FETCHER_THREADS = 12

def handle_stock_info(db, stock, stock_info):
	dbhandler.insert_market_if_needed(db, stock_info.get_stock_exchange())
	dbhandler.store_stock_info(db, stock, stock_info)
	dbhandler.store_stock_prices(db, stock, stock_info)

def handle_index_info(db, index, index_info):
	dbhandler.insert_market_if_needed(db, index_info.get_stock_exchange())
	dbhandler.store_index_info(db, index, index_info)
	dbhandler.store_index_prices(db, index, index_info)

def fetch_and_handle_stock_info(thread_id, db, stocks):
	for stock in stocks:
		log.info(log.FETCHER_SCRIPT_LOG_FILE, 'Thread ' + thread_id + ' fetching stock info for ticker: ' + stock)
		stock_info = YahooFinancials(stock)
		stock_exchange = ''
		try:
			stock_exchange = stock_info.get_stock_exchange()
		except Exception as e:
			log.error(log.FETCHER_SCRIPT_LOG_FILE, 'Thread ' + thread_id + ' was unable to store stock information for ticker: ' + stock + ', failed to resolve stock exchange')
			log.error(log.FETCHER_SCRIPT_LOG_FILE, 'Exception: ' + str(e))

		if (stock_exchange != ''):
			handle_stock_info(db, stock, stock_info)

def fetch_and_handle_index_info(thread_id, db, indices):
	for index in indices:
		log.info(log.FETCHER_SCRIPT_LOG_FILE, 'Thread ' + thread_id + ' fetching info for index: ' + index)
		index_info = YahooFinancials(index)
		stock_exchange = ''
		try:
			stock_exchange = index_info.get_stock_exchange()
		except Exception as e:
			log.error(log.FETCHER_SCRIPT_LOG_FILE, 'Thread ' + thread_id + ' was unable to store index information for: ' + index + ', failed to resolve index exchange')
			log.error(log.FETCHER_SCRIPT_LOG_FILE, 'Exception: ' + str(e))

		if (stock_exchange != ''):
			handle_index_info(db, index, index_info)

def do_stock_info_fetching(thread_id, stocks):
	log.info(log.FETCHER_SCRIPT_LOG_FILE, 'Starting thread-id: ' + thread_id)
	db = dbhandler.connect_to_database(thread_id)
	fetch_and_handle_stock_info(thread_id, db, stocks)
	dbhandler.close_connection_to_database(thread_id, db)
	log.info(log.FETCHER_SCRIPT_LOG_FILE, 'Exiting thread-id: ' + thread_id)

def do_index_info_fetching(thread_id, indices):
	log.info(log.FETCHER_SCRIPT_LOG_FILE, 'Starting thread-id: ' + thread_id)
	db = dbhandler.connect_to_database(thread_id)
	fetch_and_handle_index_info(thread_id, db, indices)
	dbhandler.close_connection_to_database(thread_id, db)
	log.info(log.FETCHER_SCRIPT_LOG_FILE, 'Exiting thread-id: ' + thread_id)

class StockFetcherThread(threading.Thread):
	def __init__(self, thread_id, stocks):
		threading.Thread.__init__(self)
		self.thread_id = thread_id
		self.stocks = stocks
	def run(self):
		do_stock_info_fetching(self.thread_id, self.stocks)

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

do_index_info_fetching('t0_fetcher_main', indices)

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

		thread = StockFetcherThread('t' + str(thread_count) + '_fetcher_worker', thread_stocks)
		thread.start()

		thread_count = thread_count + 1
else:
	start_stock_info_fetching('t0_fetcher_main', stocks)
