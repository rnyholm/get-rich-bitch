#!/usr/bin/env python
import MySQLdb
import localtime
import logger as log

# Database connection
SQL_HOST = '35.231.26.118'
SQL_USER = 'petroleum'
SQL_PSWD = 'petroleum'
SQL_DB = 'stockdata'

def connect_to_database(thread_id):
	'''
		To get a connection to a MySQL instance.

		Arguments
		---------
		thread_id: ID of the thread connecting to database
	'''
	db = MySQLdb.connect(host=SQL_HOST, user=SQL_USER, passwd=SQL_PSWD, db=SQL_DB)
	log.info(log.SQL_LOG_FILE, 'Thread: ' + thread_id + ', connected to database: ' + SQL_DB + ', on host: ' + SQL_HOST + str(db))
	return db

def close_connection_to_database(thread_id, db):
	'''
		To close a connection to a MySQL instance.

		Arguments
		---------
		thread_id: ID of the thread closing connection to database
		db: MySQL instance, connection, to be closed
	'''
	db.close()
	log.info(log.SQL_LOG_FILE, 'Thread: ' + thread_id + ', closed connection to database: ' + SQL_DB + ', on host: ' + SQL_HOST)

def execute_sql_with_logging(cursor, sql):
	'''
		To execute SQL with logging against given database.

		Arguments
		---------
		cursor: Cursor on which SQL will be executed
		sql: SQL to be executed
	'''
	log.info(log.SQL_LOG_FILE, 'Executing sql: ' + sql)
	return cursor.execute(sql)

def insert_market_if_needed(db, market):
	'''
		Inserts market into the databases market table if needed,
		read if it doesn't exist.

		Arguments
		---------
		db: MySQL db instance to which given market will be inserted
		market: market to be inserted if it doesn't exist
	'''
	cursor = db.cursor()
	sql = "SELECT * FROM markets WHERE market = '{}'".format(market)
	number_of_markets = execute_sql_with_logging(cursor,sql) # Maximum one result row due to PK constraint in markets table
	if (number_of_markets == 0):
		sql = "INSERT INTO markets VALUES('{}')".format(market)
		execute_sql_with_logging(cursor, sql)
		db.commit()

def store_stock_info(db, stock, stock_info):
	'''
		Stores stock info, if it exists, the info will be updated.

		Arguments
		---------
		db: MySQL db instance to which given stock info will be stored
		stock: stock, or ticker, to be stored
		stock_info: information to be stored
	'''
	cursor = db.cursor()
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

def store_stock_prices(db, stock, stock_info):
	'''
		Stores stock prices, one entry per day will be inserted. If an entry
		exists in the database the entry will be updated with current price.

		Arguments
		---------
		db: MySQL db instance to which given stock info(prices) will be stored
		stock: stock to be stored
		stock_info: information(prices) to be stored
	'''
	cursor = db.cursor()
	sql = "SELECT * FROM stocks s JOIN prices p ON s.ticker = p.ticker WHERE s.ticker = '{}' AND p.date LIKE '{}'".format(stock, localtime.get_timestamp_for_sql_select())
	number_of_prices = execute_sql_with_logging(cursor, sql)
	if (number_of_prices == 0): # Doesn't exist any prices, insert fresh ones
		sql = "INSERT INTO prices (ticker, date, previousclose, open, low, high, volume, daytrend) VALUES('{}', '{}', {}, {}, {}, {}, '{}', '{}')" \
		.format(stock, localtime.get_timestamp_for_sql_insert(), stock_info.get_prev_close_price(), stock_info.get_open_price(), stock_info.get_daily_low(), stock_info.get_daily_high(), stock_info.get_current_volume(), stock_info.get_current_price())
		execute_sql_with_logging(cursor, sql)
		db.commit()
	elif (number_of_prices == 1): # Update prices
		stock_and_prices_result = cursor.fetchall()
		stock_and_prices = stock_and_prices_result[0] # Should be exactly one!
		daytrend =  str(stock_and_prices[12]) + ';{}'.format(stock_info.get_current_price())
		sql = "UPDATE prices SET date = '{}', previousclose = {}, open = {}, low = {}, high = {}, volume = '{}', daytrend = '{}' WHERE id = {}"	\
		.format(localtime.get_timestamp_for_sql_insert(), stock_info.get_prev_close_price(), stock_info.get_open_price(), stock_info.get_daily_low(), stock_info.get_daily_high(), stock_info.get_current_volume(), daytrend, stock_and_prices[3])
		execute_sql_with_logging(cursor, sql)
		db.commit()
	else: # This is wrong, we should only have exactly one result row
		log.error(log.SQL_LOG_FILE, 'There exists more than one price-row for ticker: ' + stock + ' and date: ' + localtime.get_timestamp_for_sql_select())

def store_index_info(db, index, index_info):
	'''
		Stores index info, if it exists, the info will be updated.

		Arguments
		---------
		db: MySQL db instance to which given index info will be stored
		index: index to be stored
		index_info: information to be stored
	'''
	cursor = db.cursor()
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

def store_index_prices(db, index, index_info):
	'''
		Stores index prices, one entry per day will be inserted. If an entry
		exists in the database the entry will be updated with current price.

		Arguments
		---------
		db: MySQL db instance to which given index info(prices) will be stored
		index: index to be stored
		index_info: information(prices) to be stored
	'''
	cursor = db.cursor()
	sql = "SELECT * FROM indices i JOIN prices p ON i.index = p.index WHERE i.index = '{}' AND p.date LIKE '{}'".format(index, localtime.get_timestamp_for_sql_select())
	number_of_prices = execute_sql_with_logging(cursor, sql)
	if (number_of_prices == 0): # Doesn't exist any prices, insert fresh ones
		sql = "INSERT INTO prices (`index`, date, previousclose, open, low, high, volume, daytrend) VALUES('{}', '{}', {}, {}, {}, {}, '{}', '{}')" \
		.format(index, localtime.get_timestamp_for_sql_insert(), index_info.get_prev_close_price(), index_info.get_open_price(), index_info.get_daily_low(), index_info.get_daily_high(), index_info.get_current_volume(), index_info.get_current_price())
		execute_sql_with_logging(cursor, sql)
		db.commit()
	elif (number_of_prices == 1): # Update prices
		index_and_prices_result = cursor.fetchall()
		index_and_prices = index_and_prices_result[0] # Should be exactly one!
		daytrend =  str(index_and_prices[11]) + ';{}'.format(index_info.get_current_price())
		sql = "UPDATE prices p  SET p.date = '{}', p.previousclose = {}, p.open = {}, p.low = {}, p.high = {}, p.volume = '{}', p.daytrend = '{}' WHERE id = {}"     \
		.format(localtime.get_timestamp_for_sql_insert(), index_info.get_prev_close_price(), index_info.get_open_price(), index_info.get_daily_low(), index_info.get_daily_high(), index_info.get_current_volume(), daytrend, index_and_prices[2])
		execute_sql_with_logging(cursor, sql)
		db.commit()
	else: # This is wrong, we should only have exactly one result row
		log.error(log.SQL_LOG_FILE, 'There exists more than one price-row for index: ' + index + ' and date: ' + localtime.get_timestamp_for_sql_select())

def fetch_price_rows_for_stock(db, stock):
	'''
		Fetches prices from the datbase for a specific stock(ticker).

		Arguments
		---------
		db: MySQL db instance from which prices will be fetched
		stock: Stock which prices is to be fetched
	'''
	cursor = db.cursor()
	sql = "SELECT * FROM prices WHERE ticker = '{}'".format(stock)
	number_of_price_rows = execute_sql_with_logging(cursor, sql)
	if (number_of_price_rows > 0):
		return cursor.fetchall()
