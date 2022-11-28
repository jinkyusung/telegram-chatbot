import telepot
import time


class EmptyUserIdError(Exception):
    """ Failed to get_user_id(bot: telepot.Bot) -> str """
    def __str__(self):
        error_msg: str = """Before call function \n\t\t\t get_user_id(bot: telepot.Bot) \n
        Start chat with Telegram bot with message"""
        return error_msg


class NotUserIdError(Exception):
    """ Request from Bot, not User. """
    def __str__(self):
        error_msg: str = """Invalid request from Bot."""
        return error_msg


def get_user_id(bot: telepot.Bot) -> str:
    try:
        resp: list = bot.getUpdates()
        is_bot: bool = resp[0]['message']['from']['is_bot']
        user_id: str = resp[0]['message']['from']['id']
        if is_bot:
            raise NotUserIdError()
        elif not user_id:
            raise EmptyUserIdError()
        else:
            return user_id
    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    token = '5892893666:AAHtz2Hum9l_5Y3pgD0FfTX8wxSZdFLCKdc'

    test_bot = telepot.Bot(token)
    my_id = get_user_id(test_bot)
    for i in range(3):
        test_bot.sendMessage(chat_id=my_id, text="Test message!")
        time.sleep(3)