#!/usr/bin/env python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress warning about incompatible processor arcitechture

import time
import MySQLdb
import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Database connection
SQL_HOST = '35.231.26.118'
SQL_USER = 'petroleum'
SQL_PSWD = 'petroleum'
SQL_DB = 'stockdata'

# File locations
DIRNAME = os.path.dirname(__file__)
SCRIPT_LOG_FILE = DIRNAME + '/log/stock-price-predictor.log'
SQL_LOG_FILE = DIRNAME + '/log/sql.log'

# Log severitys
LOG_SEVERITY_INFO = 'INFORMATION'
LOG_SEVERITY_WARNING = 'WARNING'
LOG_SEVERITY_ERROR = 'ERROR'

#Timezone offset
os.environ['TZ'] = 'Europe/Helsinki'
time.tzset()

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
	log(SCRIPT_LOG_FILE, LOG_SEVERITY_INFO, 'Thread: ' + thread_id + ', closed connection to database: ' + SQL_DB + ', on host: ' + str(SQL_HOST))

def execute_sql_with_logging(cursor, sql):
	log(SQL_LOG_FILE, LOG_SEVERITY_INFO, 'Executing sql: ' + sql)
	return cursor.execute(sql)

def get_price_data_for_ticker(ticker):
	db = connect_to_database('predictor-main')
	cursor = db.cursor()
	
	sql = "SELECT * FROM prices WHERE ticker = '{}'".format(ticker)
	number_of_price_rows = execute_sql_with_logging(cursor, sql)
	if (number_of_price_rows > 0):
		price_rows = cursor.fetchall()
		for price_row in price_rows:
			print(str(price_row[0]) + " " + str(price_row[1]) + " " + str(price_row[2]) + " " + str(price_row[3]) + " " + str(price_row[4]) + " " + str(price_row[5]) + " " + str(price_row[6]))

get_price_data_for_ticker('YIT.HE')

