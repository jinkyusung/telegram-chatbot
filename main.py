import telepot
from telepot.loop import MessageLoop

from selenium import webdriver
from selenium.webdriver.common.by import By

import pybithumb
import mplfinance as mpf

import os
import time
import collections


class Message:
    pass


class Escort(Message):

    @staticmethod
    def get_user_name():
        resp: list = bot.getUpdates()
        return resp[0]['message']['from']['first_name']

    @staticmethod
    def welcome():
        msg = f"Hi👋, {Escort.get_user_name()}.\n" \
              + "I'm Cryptocurrency information bot.\n" \
              + "If you want to see all control *commands*, sending */help*"
        return msg

    @staticmethod
    def help():
        msg = "You can control me by sending these\n*commands*:\n"\
                + "`()` are necessary arguments.\n\n"\
                + "*/list* : show all cryptocurrency list in bithumb\n\n"\
                + "*/price* `(code)` : show current price of cryptocurrency\nex) /price BTC\n\n"\
                + "*/relation* `(code)` : show top10 related of your cryptocurrency\nex) /relation BTC\n\n"\
                + "*/chart* `(code) (k) `\n: show *candlestickchart* of cryptocurrency last k (positive int) days.\n"
        return msg

    @staticmethod
    def invalid(user_input):
        msg = f"🚫*Error* : {user_input} is _invalid_ command.\n"\
            + "To see valid *commands*, sending */help*"
        return msg

    @staticmethod
    def invalid_code(code):
        if not code:
            msg = f"🚫*Error* : /chart `CODE` 👈 Plz input cryptocurrency code name into `CODE`.\n" \
                  + "You can check all existing cryptocurrency code list by typing\n" \
                  + "*/list*\n" \
                  + "command."
        else:
            msg = f"🚫*Error* : /chart `{code}` 👈 `{code}` is Non-exist cryptocurrency code name.\n"\
                + "Please input *existing cryptocurrency code name*.\n"\
                + "You can check all existing cryptocurrency code list by typing\n"\
                + "*/list*\n"\
                + "command."
        return msg


class Chart(Message):
    @staticmethod
    def save_img(code, k=10):
        df = pybithumb.get_ohlcv(code)
        all = len(df.index.to_list())
        mpf.plot(df.iloc[all - min(1+k, all):all], volume=True,style='yahoo',type='candle', savefig=f"./{code}.png")
        print(f'Chart img saved as {code}.png')
        return


class CryptoList(Message):

    @staticmethod
    def get_prefix(payment_currency='KRW'):
        res = pybithumb.get_tickers(payment_currency)
        return sorted(set(map(lambda x: x[0], res)))

    @staticmethod
    def get_total_num(payment_currency='KRW'):
        res = pybithumb.get_tickers(payment_currency)
        return len(res)

    @staticmethod
    def welcome():
        msg = f"*[Cryptocurrency List in Bitumb]* _KRW_\n\n"
        return msg

    @staticmethod
    def goodbye():
        msg = "*Done!*\n"\
              + f"Total num : *{CryptoList.get_total_num()}*"
        return msg
        
    @staticmethod
    def show(prefix, payment_currency='KRW'):
        res = pybithumb.get_tickers(payment_currency)
        name_dict = collections.defaultdict(list)
        for name in sorted(res):
            name_dict[name[0]].append(name)
        msg = f"{prefix}\n"
        for name in name_dict[prefix]:
            msg += f"[{name}](https://www.bithumb.com/trade/order/{name}_{payment_currency})    "
        return msg

    @staticmethod
    def current_price(coin_name, payment_currency='KRW'):
        url = 'https://www.bithumb.com/trade/order/' + coin_name + '_'+ payment_currency
        driver = webdriver.Chrome('chromedriver')
        print(url)
        driver.get(url)
        bring_cur_price = driver.find_element(By.CLASS_NAME, 'current_price')
        real_cur_price = bring_cur_price.find_element(By.TAG_NAME, 'h3').text
        msg = f"{coin_name}'s current price : {real_cur_price}\n"
        return msg
    
    @staticmethod
    def relation_ranking(coin_name, res):
        con_key = ""
        sec_key = ""
        bithumb = pybithumb.Bithumb(con_key, sec_key)
        my_df_open = bithumb.get_candlestick(coin_name, chart_intervals="1m")['open'].values.tolist()
        my_diff = percent(my_df_open)
        all = pybithumb.get_current_price("ALL")
        my_fluctate_rate = all[coin_name]['fluctate_rate_24H']
        top10_temp = {}
        for k, v in all.items():
            top10_temp[k] = abs(float(v['fluctate_rate_24H'])-float(my_fluctate_rate))
        top10_list = sorted(top10_temp.items(), key=lambda item: item[1])[:11]
        top10 = {}
        for i in top10_list:
            ticker = i[0]
            ticker_open = bithumb.get_candlestick(ticker, chart_intervals="1m")['open'].values.tolist()
            ticker_diff = percent(ticker_open)
            ticker_score = 0
            for j in range(len(my_diff)):
                if my_diff[j]*ticker_diff[j] > 0:
                    ticker_score += 1
            top10[ticker] = ticker_score
        top10 = sorted(top10.items(), key=lambda item: item[1], reverse=True)

        msg = f"for recent 25H, these are top10 rankings of 'related of {coin_name}' \n"

        for rank in range(len(top10)):
            ticker = top10[rank][0]
            score = top10[rank][1]
            if rank == 0:
                my_score = score
                msg += f"standard is {ticker} {score}\n-----------------------------\n"
            else:
                msg += f"{rank} *{ticker}* {score} ({int(score*100/my_score)}%)\n"
        msg += f"-----------------------------\n(If it rises or falls with {coin_name} at the same time, score is high. - checking every minute)"
        return msg


def percent(open_price):
    diff = []
    for i in range(len(open_price)-1):
        diff.append(100*(open_price[i+1]-open_price[i])/open_price[i])
    return diff


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == "text":
        user_input = msg["text"]
        # class Escort
        if user_input == "/start":
            bot.sendMessage(
                chat_id=chat_id, parse_mode='Markdown', text=Escort.welcome()
            )
        elif user_input == "/help":
            bot.sendMessage(
                chat_id=chat_id, parse_mode='Markdown', text=Escort.help()
            )
        # class CrpytoList
        elif user_input == "/list":
            bot.sendMessage(
                chat_id=chat_id, parse_mode='Markdown', text=CryptoList.welcome()
            )
            for prefix in CryptoList.get_prefix():
                bot.sendMessage(
                    chat_id=chat_id,parse_mode='Markdown',
                    text=CryptoList.show(prefix), disable_web_page_preview=True
                )
            bot.sendMessage(
                chat_id=chat_id, parse_mode='Markdown', text=CryptoList.goodbye()
            )
        elif user_input[:6] == "/price" and len(user_input) > 7:
            res = pybithumb.get_tickers('KRW')
            if user_input[6] == ' ' and user_input[7:] in res:
                bot.sendMessage(
                    chat_id=chat_id, parse_mode='Markdown', text=CryptoList.current_price(user_input[7:])
                )
            else:
                bot.sendMessage(
                    chat_id=chat_id,
                    parse_mode='Markdown',
                    text=Escort.invalid(user_input)
                )
        elif user_input[:9] == '/relation' and len(user_input) > 10:
            res = pybithumb.get_tickers('KRW')
            if user_input[9] == ' ' and user_input[10:] in res:
                bot.sendMessage(
                    chat_id=chat_id, parse_mode='Markdown', text=CryptoList.relation_ranking(user_input[10:], res)
                )
            else:
                bot.sendMessage(
                    chat_id=chat_id,
                    parse_mode='Markdown',
                    text=Escort.invalid(user_input)
                )
        # class Chart
        elif user_input[:6] == '/chart':
            cmd = user_input[6:].split()
            if not cmd:
                bot.sendMessage(
                    chat_id=chat_id,
                    parse_mode='Markdown',
                    text=Escort.invalid(user_input)
                )
            elif len(cmd) == 1:
                payment_currency = 'KRW'
                code = cmd[0]
                if code in set(pybithumb.get_tickers(payment_currency)):
                    Chart.save_img(code)
                    bot.sendPhoto(chat_id, photo=open(f'{code}.png', 'rb'))
                    file_path = f'{code}.png'
                    os.remove(file_path)
                else:
                    bot.sendMessage(
                        chat_id=chat_id,
                        parse_mode='Markdown',
                        text=Escort.invalid_code(code)
                    )
            elif len(cmd) == 2:
                payment_currency = 'KRW'
                code = cmd[0]
                if code in set(pybithumb.get_tickers(payment_currency)) \
                        and cmd[1].isdigit():
                    Chart.save_img(code, int(cmd[1]))
                    bot.sendPhoto(chat_id, photo=open(f'{code}.png', 'rb'))
                    file_path = f'{code}.png'
                    os.remove(file_path)
                else:
                    bot.sendMessage(
                        chat_id=chat_id,
                        parse_mode='Markdown',
                        text=Escort.invalid(user_input)
                    )
            else:
                bot.sendMessage(
                    chat_id=chat_id,
                    parse_mode='Markdown',
                    text=Escort.invalid(user_input)
                )
        # invalid case
        else:
            bot.sendMessage(
                chat_id=chat_id,
                parse_mode='Markdown',
                text=Escort.invalid(user_input)
            )


if __name__ == '__main__':
    token = "5725633579:AAGi5WMEJ_7Dg0P4WXsQnIS_0uK1yae_Wiw"
    bot = telepot.Bot(token)
    MessageLoop(bot, handle).run_as_thread()
    while 1:
        time.sleep(10)
        