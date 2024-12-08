

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



