# get-rich-bitch
Experimental project which objectives are to fetch information from some predefined stocks. Keyvalues will be stored in a database and in the long run some kind of machine learning will be used to predict if a stock will go up in the near future.

## Workflow

### Fetching stock information
The script `stock-price-fetcher.py` fetches prices and other stock info from a set of predefined tickers. 
These tickers are set in `conf`-folder as  files named like `market.stx`, eg. definition file for Helsinki market tickers will be named as `hel.stx`. This file is configured as 'one-ticker-per-row'.
Since this script uses the module https://github.com/JECSand/yahoofinancials for alla data fetchong from Yahoo, it's necessary that the tickers are named in a way that Yahoo can interpret.

This script is triggered by a cron job and could be configured like someting like this
> `*/30 9-19 * * 0-4 /usr/local/bin/get-rich-bitch/stock-price-fetcher.py`

### Storing stock specific data
The fetched data will then be stored in a `cloud SQL` database by the same script, `stock-price-fetcher.py` for later handling.

### Machine-learning and prediction
Another job will contiously analyze this stored data and using some kind of machine-learning and training it will be able to deliver a report with predicions with stocks that most likely will go up in price in the near future.
