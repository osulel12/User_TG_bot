from telebot import types
import typing


def create_replay_markup(message_text: str, state: str) -> types.ReplyKeyboardMarkup:
    """
    Генерирует набор кнопок клавиатуры в зависимости от переданных параметров

    :param message_text: сообщение от пользователя
    :param state: состояние, в котором сейчас находится пользователь
    :return: сгенерированную клавиатуру
    """

    if message_text == '' and state == 'main':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('📤 Аналитика внешних рынков')
        btn2 = types.KeyboardButton('🚧 Тарифные/Нетарифные барьеры')
        btn3 = types.KeyboardButton('🏞 Региональная аналитика')
        btn4 = types.KeyboardButton('📩 Управление рассылкой')
        btn5 = types.KeyboardButton('🤖 Что умеет бот')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        return markup
    elif message_text in ['📤 Аналитика внешних рынков', '🔙 Назад'] and state == 'analist':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('📜 Страновые справки')
        btn3 = types.KeyboardButton('🚪 В главное меню')
        markup.add(btn1, btn3)
        return markup
    elif message_text == '📜 Страновые справки' and state == 'analist':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('📔 Перечень стран')
        btn2 = types.KeyboardButton('📕 Перечень групп')
        btn3 = types.KeyboardButton('🔙 Назад')
        markup.add(btn1, btn2, btn3)
        return markup
    elif message_text in ['🚧 Тарифные/Нетарифные барьеры', '🔙 Назад'] and state == 'barier':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('📑 Ветеринарные сертификаты')
        btn2 = types.KeyboardButton('❗️ Обзор барьеров по странам')
        btn4 = types.KeyboardButton('🚪 В главное меню')
        markup.add(btn1, btn2, btn4)
        return markup
    elif message_text == '📑 Ветеринарные сертификаты' and state == 'barier':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('📭 Сертификаты без ссылок')
        btn2 = types.KeyboardButton('📬 Сертификаты со ссылками')
        btn3 = types.KeyboardButton('↕️ История изменений сертификатов')
        btn4 = types.KeyboardButton('🔍 Запуск проверки сертификатов')
        btn5 = types.KeyboardButton('🔙 Назад')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        return markup
    elif message_text == '❗️ Обзор барьеров по странам' and state == 'barier':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('🌍 Список стран')
        btn4 = types.KeyboardButton('🔙 Назад')
        markup.add(btn1, btn4)
        return markup
    elif message_text in ['🏞 Региональная аналитика', '🔙 Назад'] and state == 'region':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('📜 Справки по форме 8')
        btn2 = types.KeyboardButton('🚪 В главное меню')
        markup.add(btn1, btn2)
        return markup
    elif message_text == '📜 Справки по форме 8' and state == 'region':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        btn1 = types.KeyboardButton('📔 Перечень регионов')
        btn2 = types.KeyboardButton('🔙 Назад')
        markup.add(btn1, btn2)
        return markup


def create_inline_markup(state: str,
                         list_itemns: typing.Optional[list | dict] = None,
                         pagen: typing.Optional[int] = 0,
                         element_on_page: typing.Optional[int] = 21,
                         country_state: typing.Optional[str] = None) -> types.InlineKeyboardMarkup:
    """
    Возвращает инлайн клавиатуру в зависимости от переданных параметров

    :param state: состояние пользователя

    :param list_itemns: набор элементов. Либо список стран/дат указанных в названии страновых справок,
                        либо словарь со странами

    :param pagen: значение на какой странице клавиатуры находится пользователь

    :param element_on_page: количество кнопок на одной странице клавиатуры

    :param country_state: страна, с которой пользователь работал крайний раз
                          необходим, для формирования уникальных callbacck
                          и предотвращения путаницы в параметрах кнопок

    :return: сформированную инлайн клавиатуру
    """

    if state in ['analist_country', 'analist_group_country']:
        # Список со странами
        lst_country = [v for v in list_itemns]
        # Список списков для создания пагинации клавитауры
        lst_pagen_country = [lst_country[i:i + element_on_page] for i in range(0, len(lst_country), element_on_page)]
        btns = []

        # Наполняем список кнопками с названиями стран
        for country in lst_pagen_country[pagen]:
            btns.append(types.InlineKeyboardButton(text=country, callback_data=country))
        markup = types.InlineKeyboardMarkup()
        markup.add(*btns)

        # Формируем элементы навигации по клавиатуре
        if pagen + 1 == 1:
            markup.add(types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
        elif pagen + 1 == len(lst_pagen_country):
            markup.add(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '))
        else:
            markup.add(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
        return markup

    elif state in ['form2_version_country', 'form1_version_country', 'form1_version_group', 'form2_version_group']:
        lst_country = list_itemns
        lst_pagen_country = [lst_country[i:i + element_on_page] for i in range(0, len(lst_country), element_on_page)]
        btns = []

        for date in lst_pagen_country[pagen]:
            btns.append(types.InlineKeyboardButton(text=date.replace('.', '-').replace('_', '-'), callback_data=date))
        markup = types.InlineKeyboardMarkup()
        markup.add(*btns)

        if len(lst_pagen_country) == 1:
            markup.add(types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '))
        elif pagen + 1 == 1:
            markup.add(types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
        elif pagen + 1 == len(lst_pagen_country):
            markup.add(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '))
        else:
            markup.add(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
        return markup

    elif state == 'form_version_country':
        markup = types.InlineKeyboardMarkup()
        # В зависимости от наличия наименований мы либо добавляем ссылки на справки по определенной
        # форме или нет
        if 'f2' in list_itemns:
            markup.add(types.InlineKeyboardButton(text='Справка по форме 2', callback_data=f'form2_version_country.{country_state}'))
        else:
            pass
        if 'f1' in list_itemns:
            markup.add(types.InlineKeyboardButton(text='Справка по форме 1', callback_data=f'form1_version_country.{country_state}'))
        else:
            pass
        return markup

    elif state == 'form_version_group':
        markup = types.InlineKeyboardMarkup()
        if 'f2' in list_itemns:
            markup.add(types.InlineKeyboardButton(text='Справка по форме 2', callback_data=f'form2_version_group.{country_state}'))
        else:
            pass
        if 'f1' in list_itemns:
            markup.add(types.InlineKeyboardButton(text='Справка по форме 1', callback_data=f'form1_version_group.{country_state}'))
        else:
            pass
        return markup

    elif state in ['barier_country']:
        lst_country = [k for k, v in list_itemns.items()]
        lst_pagen_country = [lst_country[i:i + element_on_page] for i in range(0, len(lst_country), element_on_page)]
        btns = []

        for country in lst_pagen_country[pagen]:
            btns.append(types.InlineKeyboardButton(text=country, callback_data=country))
        markup = types.InlineKeyboardMarkup()
        markup.add(*btns)

        if pagen + 1 == 1:
            markup.add(types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
        elif pagen + 1 == len(lst_pagen_country):
            markup.add(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '))
        else:
            markup.add(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
        return markup

    elif state in ['region_reference']:
        list_region = [k for k, v in list_itemns.items()]
        lst_pagen_country = [list_region[i:i + element_on_page] for i in range(0, len(list_region), element_on_page)]
        btns = []

        for country in lst_pagen_country[pagen]:
            btns.append(types.InlineKeyboardButton(text=country, callback_data=country))
        markup = types.InlineKeyboardMarkup()
        markup.add(*btns)

        if pagen + 1 == 1:
            markup.add(types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
        elif pagen + 1 == len(lst_pagen_country):
            markup.add(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '))
        else:
            markup.add(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_country)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
        return markup

    elif state in ['subscribe']:
        btns = []
        # {'alert_id': 2, 'type_alert': 'Обновление данных в БД', 'status_alert': True}
        lst_pagen_alert = [list_itemns[i:i + element_on_page] for i in range(0, len(list_itemns), element_on_page)]
        for i in lst_pagen_alert[pagen]:
            btns.append(types.InlineKeyboardButton(text=f"{'✅' if i['status_alert'] else '❌'} {i['type_alert']}", callback_data=i['alert_id']))
        btns = sorted(btns, key=lambda x: len(x.text))
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(*btns)

        if len(lst_pagen_alert) == 1:
            markup.row(types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_alert)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'🚪 В главное меню', callback_data=f'main'))
        elif pagen + 1 == 1 and len(lst_pagen_alert) > 1:
            markup.row(types.InlineKeyboardButton(text=f'🚪 В главное меню', callback_data=f'main'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_alert)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
        elif pagen + 1 == len(lst_pagen_alert) and len(lst_pagen_alert) > 1:
            markup.row(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_alert)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'🚪 В главное меню', callback_data=f'main'))
        elif 1 < pagen + 1 < len(lst_pagen_alert) and len(lst_pagen_alert) > 1:
            markup.row(types.InlineKeyboardButton(text=f'⬅', callback_data=f'back'),
                       types.InlineKeyboardButton(text=f'{pagen + 1}/{len(lst_pagen_alert)}', callback_data=f' '),
                       types.InlineKeyboardButton(text=f'➡', callback_data=f'next'))
            markup.row(types.InlineKeyboardButton(text=f'🚪 В главное меню', callback_data=f'main'))

        return markup
