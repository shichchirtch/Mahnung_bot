from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def titel_check(name: str) -> str:
    if isinstance(name, str):
        return name
    raise ValueError


def id_check(id_mahnung:str) ->str:
    if id_mahnung.isdigit() and 2<len(id_mahnung)<11:
        return id_mahnung
    raise ValueError


def return_right_row(stroka:str)->str:
    # print('syroka = ', stroka)
    cut_stroka = stroka[:-7]
    # print('cut_str = ', cut_stroka)
    if len(cut_stroka)>2:
        new_s = cut_stroka.split(', ')
        data  =sorted(map(int,new_s))
        s = ''
        for x in data:
            s+=str(x) + ', '
        ret_str = s[:-2] + stroka[-6:]
        # print('ret_str = ', ret_str)
        return ret_str

    else:
        return stroka

def week_day_bearbeiten(digit_list:list):
    new_list = sorted(digit_list)
    week_dict = {0:'Monday', 1:'Tuesday', 2:'Wensday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
    s = ''
    for x in new_list:
        s+=week_dict[int(x)] + ', '
    return s[:-2]

def seconds_to_date_string(lst_str):
    arr = []
    for sobitie in lst_str:
        date = datetime.utcfromtimestamp(int(sobitie))
        liter_data = date.strftime("%Y-%m-%d")
        arr.append(liter_data)
    # print('arr = ', arr)
    return arr


def create_past_mahnung_keyboard(len_mahnung_picture_list: int, page=1 ) -> InlineKeyboardMarkup:
    print('page = ', page)
    forward_button = InlineKeyboardButton(text=f'Total {len_mahnung_picture_list}  >>', callback_data='forward')
    backward_button = InlineKeyboardButton(text=f'<< {page+1}', callback_data='backward')
    exit_button = InlineKeyboardButton(text=f'◀️', callback_data='exit_from_past_bild_mahnung')
    pagination_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[exit_button], [backward_button, forward_button]])
    return pagination_keyboard

