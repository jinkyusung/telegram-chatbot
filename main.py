import telepot
from telepot.loop import MessageLoop
import time
import pybithumb
import collections
from selenium import webdriver
from selenium.webdriver.common.by import By
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
        msg = "You can control me by sending these\n*commands*:\n\n"\
              + "*/list* : show all cryptocurrency list in bithumb\n"\
                + "*/price (bitcoin name)* : show current price of bitcoin\nex) /price BTC\n"\
                + "*/relation (bitcoin name)* : show top10 related of your bitcoin\nex) /relation BTC\n"
        return msg
    @staticmethod
    def invalid(user_input):
        msg = f"🚫*Error* : {user_input} is _invalid_ command.\n"\
            + "To see valid *commands*, sending */help*"
        return msg
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
        # invalid case
        else:
            bot.sendMessage(
                chat_id=chat_id,
                parse_mode='Markdown',
                text=Escort.invalid(user_input)
            )


if __name__ == '__main__':
    token = ""

    bot = telepot.Bot(token)
    MessageLoop(bot, handle).run_as_thread()
    while 1:
        time.sleep(10)