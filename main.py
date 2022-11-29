import telepot
from telepot.loop import MessageLoop
import time
import pybithumb
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
        msg = "You can control me by sending these\n*commands*:\n\n"\
              + "*/list* : show all cryptocurrency list in bithumb"
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
