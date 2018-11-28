#!/usr/bin/env python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf

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
                print(result)
