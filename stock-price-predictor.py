#!/usr/bin/env python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Suppress warning about incompatible processor arcitechture

import logger as log
import dbhandler
import tensorflow as tf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

MAIN_THREAD = 't0_predictor_main'
stock = 'NDA-FI.HE'

log.info(log.PREDICTOR_SCRIPT_LOG_FILE, 'Starting thread-id: ' + MAIN_THREAD)
db = dbhandler.connect_to_database(MAIN_THREAD)
price_rows = dbhandler.fetch_price_rows_for_stock(db, stock)

if (price_rows is None):
	log.warning(log.PREDICTOR_SCRIPT_LOG_FILE, 'No prices exists for stock: ' + stock)
else:
	for price_row in price_rows:
		log.info(log.PREDICTOR_SCRIPT_LOG_FILE, str(price_row[0]) + " " + str(price_row[1]) + " " + str(price_row[2]) + " " + str(price_row[3]) + " " + str(price_row[4]) + " " + str(price_row[5]) + " " + str(price_row[6]))

dbhandler.close_connection_to_database(MAIN_THREAD, db)

# Do some tensorflowstuff, just for fun
# Define a and b as placeholders
a = tf.placeholder(dtype=tf.int64)
b = tf.placeholder(dtype=tf.int64)
 # Define the addition
c = tf.multiply(a, b)
epochs = 30
result = 1
with tf.Session() as session:
	for epoch in range(epochs):
		result = session.run(c, feed_dict={a: result, b: 2})
		log.info(log.PREDICTOR_SCRIPT_LOG_FILE, 'Tensor-result: ' + str(result))

log.info(log.PREDICTOR_SCRIPT_LOG_FILE, 'Exiting thread-id: ' + MAIN_THREAD)
