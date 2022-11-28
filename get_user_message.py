import telepot


def get_user_message(msg):
    correct_keywords: set = {'curr_price', 'five_days_moving_avg'} #### <- improve with GUI...?
    if msg not in correct_keywords:
        beep: str = "Not correct keywords. Please input : s.t. [][][]"
        return beep


if __name__ == '__main__':
    pass