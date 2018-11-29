#!/usr/bin/env python
import os
import localtime

# File locations
DIRNAME = os.path.dirname(__file__)
FETCHER_SCRIPT_LOG_FILE = DIRNAME + '/log/stock-price-fetcher.log'
PREDICTOR_SCRIPT_LOG_FILE = DIRNAME + '/log/stock-price-predictor.log'
SQL_LOG_FILE = DIRNAME + '/log/sql.log'

# Log severitys
LOG_SEVERITY_INFO = 'INFORMATION'
LOG_SEVERITY_WARNING = 'WARNING'
LOG_SEVERITY_ERROR = 'ERROR'

# Log level
# 0 = INFORMATION
# 1 = WARNING
# 2 = ERROR
LOG_LEVEL = 0

def get_severity_string(severity):
	'''
		To get severity in text format from a numeric one.

		Arguments
		---------
		severity: numeric value indicating severity
	'''
	if (severity == 0):
		return LOG_SEVERITY_INFO
	elif (severity == 1):
		return LOG_SEVERITY_WARNING
	else:
		return LOG_SEVERITY_ERROR

def log(log_file, severity, message):
	'''
		Logs a message with severity to a specific log file.

		Arguments
		---------
		log_file: location and name of log file
		severity: severity of the log entry
		message: message of the log entry
	'''
	if (severity >= LOG_LEVEL):
		with open(log_file, 'a') as log:
			log.write(localtime.get_timestamp_for_log())
			log.write('\t')
			log.write('[' + get_severity_string(severity) + ']')
			log.write('\t')
			log.write(message)
			log.write('\n')

def info(log_file, message):
	'''
		Logs a message with INFORMATION severity to a specific log file.

		Arguments
		---------
		log_file: location and name of log file
		message: message of the log entry
	'''
	log(log_file, 0, message)

def warning(log_file, message):
	'''
		Logs a message with WARNING severity to a specific log file.

		Arguments
		---------
		log_file: location and name of log file
		message: message of the log entry
	'''
	log(log_file, 1, message)


def error(log_file, message):
	'''
		Logs a message with ERROR severity to a specific log file.

		Arguments
		---------
		log_file: location and name of log file
		message: message of the log entry
	'''
	log(log_file, 2, message)
