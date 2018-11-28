#!/usr/bin/env python
import os, shutil

# Get relative log dir
log_dir = os.path.dirname(__file__) + '/log'

for content in os.listdir(log_dir):
	path = os.path.join(log_dir, content)
	try:
		if (os.path.isfile(path)):
			os.unlink(path)
		elif (os.path.isdir(path)):
			shutil.rmtree(path)
	except Exception as e:
		print('Failed to remove path: ' + path)
		print(e)
