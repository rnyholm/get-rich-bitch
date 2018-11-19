#!/usr/bin/env python
import os
import time
import threading

from yahoofinancials import YahooFinancials
STOCK_FILES = [ '/usr/local/bin/get-rich-bitch/hel.stx' ]
LOG_FILE = '/usr/local/bin/get-rich-bitch/stock.log'
STOCK_INFO_FETCHER_THREADS = 12

#Timezone offset
os.environ['TZ'] = 'Europe/Helsinki'
time.tzset()

# Script functions and classes declaration
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

def fetch_and_log_stocks(thread_id, stocks):
	for stock in stocks:
		print 'Thread \"' + thread_id + '\" fetching stock info for ticker -> ' + stock
		stock_info = YahooFinancials(stock)
		log_stock_info(stock, stock_info)

class StockFetcherThread (threading.Thread):
	def __init__(self, thread_id, stocks):
		threading.Thread.__init__(self)
		self.thread_id = thread_id
		self.stocks = stocks
	def run(self):
		print 'Starting thread-id: ' + self.thread_id
		fetch_and_log_stocks(self.thread_id, self.stocks)
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

