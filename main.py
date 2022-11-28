import pybithumb
import time
import pandas as pd
#import xgboost as xgb
import telepot

key = 'fd2dbb1200fb2e9c1108662906941412'
secret = 'e7d61d7219d6afaf40877ae79d8b91ab'
bithumb = pybithumb.Bithumb(key, secret)

tickers = bithumb.get_tickers() #비트코인 목록들
orderbook = pybithumb.get_orderbook('BTC')  #호가 창
print(orderbook)
