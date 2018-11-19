#!/usr/bin/env python
import os
import time

from yahoofinancials import YahooFinancials

STOCK_FILES = [ '/usr/local/bin/get-rich-bitch/hel.stx' ]
LOG_FILE = '/usr/local/bin/get-rich-bitch/stock.log'

#Timezone offset
os.environ['TZ'] = 'Europe/Helsinki'
time.tzset()

for stock_file in STOCK_FILES:
	with open(stock_file, 'r') as current_stock_file:
		stocks = []
		for line in current_stock_file:
			stocks.append(line.strip('\n'))

for stock in stocks:
	# print('Fetching stock info for ticker -> ' + stock)
	stock_info = YahooFinancials(stock)
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
