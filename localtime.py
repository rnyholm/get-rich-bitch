#!/usr/bin/env python
import os
import time

#Timezone offset
os.environ['TZ'] = 'Europe/Helsinki'
time.tzset()

def get_timestamp_for_log():
	'''
		To get a timestamp in Europe/Helsinki time zone for logging.
		eg. Thu Nov 29 10:00:03 2018
	'''
	return time.asctime(time.localtime(time.time()))

def get_timestamp_for_sql_insert():
	'''
		To get a timestamp in Europe/Helsinki time zone for sql insert queries.
		eg. 2018-11-29 10:01:40
	'''
	now = time.localtime(time.time())
	return str(time.strftime("%Y-%m-%d %H:%M:%S", now))

def get_timestamp_for_sql_select():
	'''
		To get a timestamp in Europe/Helsinki time zone, appended with wildcard
		character '%' for sql select queries.
		eg. 2018-11-29%
	'''
	now = time.localtime(time.time())
	return str(time.strftime("%Y-%m-%d", now)) + '%'
