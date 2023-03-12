import random
import asyncio
from aiogram import types
from time import time
from datetime import datetime
from math import ceil
    less = 15
    more = 30
    lessair = 90
    moreair = 120
    lesstrain = 30
    moretrain = 60
    lessbus = 5
    morebus = 20
    async def battle(message, a, oth):
        try:
            if a == oth:
                await message.answer('&#10060; <i>Так нечестно. Воевать с самим собой нельзя</i>', parse_mode='html')
                return
            cursor.execute('SELECT ready FROM userdata WHERE user_id=?', (a,))
            ready = cursor.fetchone()[0]
            cursor.execute('SELECT ready FROM userdata WHERE user_id=?', (oth,))
            oready = cursor.fetchone()[0]
            cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (oth,))
            onick = cursor.fetchone()[0]
            cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (oth,))
            orasa = cursor.fetchone()[0]
            cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
            nick = cursor.fetchone()[0]
            cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
            rasa = cursor.fetchone()[0]
            cursor.execute('SELECT lastfight FROM userdata WHERE user_id = ?', (a,))
            lastfight = cursor.fetchone()[0]
            cursor.execute('SELECT lastfight FROM userdata WHERE user_id = ?', (oth,))
            olastfight = cursor.fetchone()[0]
            now = current_time()
            diff = now-lastfight
            odiff = now-olastfight
            if diff<fightlim or odiff<fightlim:
                if fightlim%60==0:
                    time = '{0}'.format(int(fightlim/60))
                    if int(time)==1:
                        time += ' минуту'
                    elif int(time)==2 or int(time)==3 or int(time)==4:
                        time += ' минуты'
                    else:
                        time += ' минут'
                else:
                    time = '{0} секунд'.format(fightlim)
                await message.answer('<i>&#10060; Бороться можно не более раза в {0}</i>'.format(time), parse_mode='html')
                return
            cursor.execute('UPDATE userdata SET battles = ? WHERE user_id=?', (oth, a,))
            conn.commit()
            cursor.execute('UPDATE userdata SET battles = ? WHERE user_id=?', (a, oth,))
            conn.commit()
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Изменить', callback_data='set_user_mode'))
            if ready == 1:
                if oready == 1:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='👊 Удар', callback_data='fight'))
                    await message.answer('<i><b><a href="tg://user?id={2}">{0}{1}</a></b>, <b><a href="tg://user?id={3}">{4}{5}</a></b>, правила таковы: кто первый нажмёт на кнопку, тот и победитель</i>'.format(orasa, onick, oth, a, rasa, nick), parse_mode = 'html', reply_markup = markup)
                    cursor.execute('UPDATE userdata SET ready = ? WHERE user_id = ?', (0,a,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET ready = ? WHERE user_id = ?', (0,oth,))
                    conn.commit()
                else:
                    await message.answer('<i><b><a href="tg://user?id={2}">{0}{1}</a></b>, <b><a href="tg://user?id={3}">{4}{5}</a></b> хочет с вами сразиться. Измените режим готовности, чтобы бой смог состояться</i>'.format(orasa, onick, oth, a, rasa, nick), parse_mode = 'html', reply_markup = markup)
            else:
                await message.reply('<i>Измените режим готовности, чтобы бой смог состояться</i>', parse_mode = 'html', reply_markup = markup)
        except Exception as e:
            await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    async def clancall(call):
        try:
            a = call.from_user.id
            chid = call.message.chat.id
            cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
            count = cursor.fetchone()[0]
            if count == 0:
                return
            if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                await main.send_message(chid, '&#10060; <i>Управлять кланом может только администратор чата</i>', parse_mode = 'html')
                return
            typ = ''
            cursor.execute('SELECT type FROM clandata WHERE group_id=?', (chid,))
            type = cursor.fetchone()[0]
            if type == 'private':
                typ = 'Частный'
            else:
                typ = 'Публичный'
            cursor.execute('SELECT place FROM userdata WHERE user_id = ?', (a,))
            place = cursor.fetchone()[0]
            cursor.execute('SELECT hqplace FROM clandata WHERE group_id = ?', (chid,))
            hqplace = cursor.fetchone()[0]
            cursor.execute('SELECT notif FROM clandata WHERE group_id = ?', (chid,))
            notf = cursor.fetchone()[0]
            notif = 'Включены' if notf==1 else 'Выключены'
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='🔐 Тип клана: {0}'.format(typ), callback_data='clan_type'))
            markup.add(types.InlineKeyboardButton(text='🔔 Уведомления: {0}'.format(notif), callback_data='clan_notifications'))
            markup.add(types.InlineKeyboardButton(text='✏ Изменить данные клана', callback_data='clan_profile'))
            if hqplace == '':
                markup.add(types.InlineKeyboardButton(text='🏢 Построить ШК: {0}'.format(place), callback_data='headquarters'))
            else:
                markup.add(types.InlineKeyboardButton(text='🏢 Снести штаб-квартиру', callback_data='clear_headquarters'))
                markup.add(types.InlineKeyboardButton(text='🏛 Локация клана', callback_data='clanlocation'))
            markup.add(types.InlineKeyboardButton(text='🏗 Постройки клана', callback_data='clan_buildings'))
            markup.add(types.InlineKeyboardButton(text='➕ Дополнения клана', callback_data='clan_plugins'))
            markup.add(types.InlineKeyboardButton(text='🖼 QR-код', callback_data='clan_qrcode'))
            markup.add(types.InlineKeyboardButton(text='🗑 Распустить клан', callback_data='delete_clan'))
            markup.add(types.InlineKeyboardButton(text='◀ Назад', callback_data='cancel_action2'))
            await main.send_message(chid, '<i>Управление кланом</i>', parse_mode = 'html', reply_markup = markup)
        except Exception as e:
            await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    async def clanprof(call):
        try:
            a = call.from_user.id
            chid = call.message.chat.id
            cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
            count = cursor.fetchone()[0]
            if count == 0:
                return
            if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                await main.send_message(chid, '&#10060; <i>Управлять кланом может только администратор чата</i>', parse_mode = 'html')
                return
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='✏ Переименовать клан', callback_data='clan_name'))
            markup.add(types.InlineKeyboardButton(text='📃 Изменить описание клана', callback_data='clan_bio'))
            markup.add(types.InlineKeyboardButton(text='🖼 Изменить фото клана', callback_data='clan_photo'))
            markup.add(types.InlineKeyboardButton(text='🔗 Изменить ссылку', callback_data='clan_link'))
            markup.add(types.InlineKeyboardButton(text='◀ Назад', callback_data='clan_settings2'))
            await main.send_message(chid, '<i>Управление кланом</i>', parse_mode = 'html', reply_markup = markup)
        except Exception as e:
            await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    async def aircall(call):
        a = call.from_user.id
        cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
        station = cursor.fetchone()[0]
        airport = ''
        markup = types.InlineKeyboardMarkup()
        if station=='Аэропорт Котай':
            airport = 'Котай'
            markup.add(types.InlineKeyboardButton(text='🛫 До Национального аэропорта', callback_data='flight'))
        elif station=='Национальный аэропорт':
            airport = 'Национальный аэропорт Живополис'
            markup.add(types.InlineKeyboardButton(text='🛫 До Котая', callback_data='flight'))
        else:
            return
        markup.add(types.InlineKeyboardButton(text='🏛 Выйти в город', callback_data='city'))
        await call.message.answer('✈ <i>Вы находитесь в аэропорту <b>{0}</b></i>'.format(airport), parse_mode = 'html', reply_markup = markup)
    async def traincall(call):
        a = call.from_user.id
        cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
        station = cursor.fetchone()[0]
        rw = ''
        stations = []
        markup = types.InlineKeyboardMarkup(row_width = 2)
        if station in ['Вокзальная', 'Александровская', 'Станция Котай']:
            for st in trains[0]:
                if st!=station:
                    ind = trains[0].index(st)
                    name = trains[1][ind]
                    stations.append(types.InlineKeyboardButton(text='🚆 {0}'.format(name), callback_data='train_{0}'.format(st)))
        else:
            for st in ['Вокзальная', 'Александровская', 'Станция Котай']:
                ind = trains[0].index(st)
                name = trains[1][ind]
                stations.append(types.InlineKeyboardButton(text='🚆 {0}'.format(name), callback_data='train_{0}'.format(st)))
        markup.add(*stations)
        markup.add(types.InlineKeyboardButton(text='🏛 Выйти в город', callback_data='city'))
        await call.message.answer('🚉 <i>Вы находитесь на станции <b>{0}</b></i>'.format(trains[2][trains[0].index(station)]), parse_mode = 'html', reply_markup = markup)
    async def regbuscall(call):
        a = call.from_user.id
        cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
        station = cursor.fetchone()[0]
        stops = []
        markup = types.InlineKeyboardMarkup(row_width = 2)
        if station in ['Автовокзал Живополис', 'АС Александрово']:
            for st in villages:
                if st!=station:
                    if st in ['Автовокзал Живополис', 'АС Александрово']:
                        stops.append(types.InlineKeyboardButton(text='🚌 {0}'.format(st), callback_data='goreg_{0}'.format(st)))
                    else:
                        stops.append(types.InlineKeyboardButton(text='🚐 {0}'.format(st), callback_data='gobus_{0}'.format(st)))
        else:
            for st in ['Автовокзал Живополис', 'АС Александрово']:	
                stops.append(types.InlineKeyboardButton(text='🚐 {0}'.format(st), callback_data='gobus_{0}'.format(st)))
        markup.add(*stops)
        markup.add(types.InlineKeyboardButton(text='🏛 Выйти в город', callback_data='city'))
        await call.message.answer('🚏 <i>Вы находитесь на остановке <b>{0}</b>\n\n❗ Стоимость одной поездки на маршрутке 🚐 составляет <b>${1}</b>, на автобусе 🚌 - <b>${2}</b></i>'.format(station, buscost, regbuscost), parse_mode = 'html', reply_markup = markup)
    async def ask(user, message):
        try:
            a = user
            now = datetime.now()
            cursor.execute('SELECT pay FROM userdata WHERE user_id = ?', (a,))
            box = cursor.fetchone()[0]
            diff = (now - datetime.fromtimestamp(0)).total_seconds() - box
            if diff >= 86400 and box != 0:
                cursor.execute('UPDATE userdata SET pay = ? WHERE user_id = ?', (0,a,))
                conn.commit()
                rand = random.randint(50,100)
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET balance = ? WHERE user_id = ?', (balance+rand, a,))
                conn.commit()
                await message.answer('<i>Ваша зарплата: <b>${0}</b>\nПриносим искренние извинения за задержку</i>'.format(rand), parse_mode = 'html')
            else:
                if box != 0:
                    h = int(24-ceil(diff/3600))
                    m = int(60-ceil(diff%3600/60))
                    s = int(60-ceil(diff%3600%60))
                    await message.answer('<i>&#10060; До зарплаты осталось {0} часов {1} минут {2} секунд </i>'.format(h,m,s), parse_mode='html')
                else:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='💼 Работать', callback_data='work'))
                    await message.answer('<i>&#10060; Вы в данный момент не работаете</i>', parse_mode='html', reply_markup = markup)
        except Exception as e:
            await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    async def work(call):
        try:
            a = call.from_user.id
            message = call.message
            now = datetime.now()
            cursor.execute('SELECT pay FROM userdata WHERE user_id = ?', (a,))
            box = cursor.fetchone()[0]
            cursor.execute('SELECT prison FROM userdata WHERE user_id = ?', (a,))
            prson = cursor.fetchone()[0]
            diff = (now - datetime.fromtimestamp(0)).total_seconds() - box
            prison = (now - datetime.fromtimestamp(0)).total_seconds() - prson
            if prison <= 86400*7:
                d = int(7-ceil(prison/86400))
                h = int(24-ceil(prison%86400/3600))
                m = int(60-ceil(prison%86400%3600/60))
                s = int(60-ceil(prison%86400%3600%60))
                await call.answer(text='👮 К сожалению, недавно вы сидели в тюрьме, и теперь у вас есть судимость. До снятия судимости осталось {0} дней {1} часов {2} минут {3} секунд'.format(d,h,m,s), show_alert = True)
                return
            if box == 0:
                cursor.execute('UPDATE userdata SET pay = ? WHERE user_id = ?', ((now - datetime.fromtimestamp(0)).total_seconds(), a,))
                conn.commit()
                await call.answer(text='💰 Вы сможете забрать свою зарплату через 24 часа', show_alert = True)
            elif diff <= 86400:
                h = int(24-ceil(diff/3600))
                m = int(60-ceil(diff%3600/60))
                s = int(60-ceil(diff%3600%60))
                await call.answer(text='❌ Вы уже работаете. До окончания осталось {0} часов {1} минут {2} секунд'.format(h,m,s), show_alert = True)
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='💰 Забрать зарплату', callback_data='salary'))
                await message.answer('<i>&#10060; Заберите свою зарплату и сможете работать снова</i>', parse_mode='html', reply_markup = markup)
        except Exception as e:
            await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')

        except Exception as e:
            await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    def access(place, userplace, stage=0):
        acc = ''
        if place in CITY:
            acc+='🚎 Остановка троллейбуса <b>{0}</b>\n'.format(place)
        for line in METRO:
            index = METRO.index(line)
            if place in line:
                if index==0 or index==2:
                    acc+='🚉 Остановка городской электрички <b>{0}</b> ({1})\n'.format(place, LINES[index].replace(' городской электрички', ''))
                else:
                    acc+='🚇 Станция метро <b>{0}</b> ({1})\n'.format(place, LINES[index])
        if place in villages:
            acc+='🚐 Автобусная остановка <b>{0}</b>\n'.format(place)
        if place in trains[0]:
            ind = trains[0].index(place)
            acc+='🚆 Остановочный пункт электропоездов <b>{0}</b> (полное название - <b>{1}</b>)\n'.format(trains[1][ind], trains[2][ind])
        if stage==0:
            for wlk in walk:
                if place in wlk:
                    ind = wlk.index(place)
                    for wnk in walk:
                        ind2 = walk.index(wnk)
                        if ind2 != walk.index(wlk) and wnk[ind]!='':
                            acc+='🚶 <b>{0}</b> секунд ходьбы до местности <b>{1}</b>'.format(walks[ind], wnk[ind])
                            ac = access(wnk[ind], place, 1)
                            if not ac=='Похоже, что такой местности не существует':
                                acc+=' и транспорта:\n⬇\n{1}'.format(wnk[ind], ac, place)
                            acc+='\n'
        if place in CITY and userplace in CITY and place!=userplace and stage==0:
            cost = abs(CITY.index(place)-CITY.index(userplace))*cabcost
            acc+='🚕 Вызов такси из местности <b>{0}</b> стоит <b>${1}</b>\n'.format(userplace, cost)
        if acc!='':
            return acc
        else:
            return 'Похоже, что такой местности не существует'
    async def buscall(call):
        try:
            a = call.from_user.id
            cursor.execute('SELECT line FROM userdata WHERE user_id=?', (a,))
            line = cursor.fetchone()[0]
            cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
            station = cursor.fetchone()[0]
            ind = CITY.index(station)
            markup = types.InlineKeyboardMarkup()
            desc = ''
            if ind == 0 or ind == len(CITY)-1:
                desc = '<b>Конечная.</b> Просьба выйти из транспортного средства'
            if ind > 0:
                prev = CITY[ind-1]
                markup.add(types.InlineKeyboardButton(text='⬅ '+prev, callback_data='trolleybus_back'))
            if ind < len(CITY)-1:
                nxt = CITY[ind+1]
                markup.add(types.InlineKeyboardButton(text='➡ '+nxt, callback_data='trolleybus_forward'))
            markup.add(types.InlineKeyboardButton(text='🏛 Выйти в город', callback_data='city'))
            route = ''
            for stat in CITY:
                if CITY.index(stat)!=0:
                    route+=', '
                if stat!=station:
                    route+=stat
                else:
                    route+='<b>{0}</b>'.format(stat)
            msg = await call.message.answer('<i><b>&#128654; Маршрут троллейбуса:</b> {2}\n\nОстановка <b>{0}</b>\n{1}</i>'.format(station, desc, route), parse_mode = 'html', reply_markup = markup)
            await asyncio.sleep(ticket_time)
            try:
                await main.delete_message(call.message.chat.id, msg['message_id'])
            except:
                pass
        except Exception as e:
            await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    async def metrocall(call):
        try:
            a = call.from_user.id
            cursor.execute('SELECT line FROM userdata WHERE user_id=?', (a,))
            line = cursor.fetchone()[0]
            cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
            station = cursor.fetchone()[0]
            ind = metro[line].index(station)
            markup = types.InlineKeyboardMarkup()
            desc = ''
            if transfer(a)!='':
                desc+='Переход к поездам {0}\n'.format(linez[transfer(a)])
            if station=='Котайский Мединститут' or (station=='Площадь Админов' and line==0) or (station=='Историческая' and line==0) or station=='Крайний Север' or station=='Северо-Восток':
                desc += '<b>Конечная.</b> Поезд дальше не идёт, просьба пассажиров выйти из вагонов'
            if ind > 0:
                prev = metro[line][ind-1]
                markup.add(types.InlineKeyboardButton(text='⬅ '+prev, callback_data='back'))
            if ind < len(metro[line])-1:
                nxt = metro[line][ind+1]
                markup.add(types.InlineKeyboardButton(text='➡ '+nxt, callback_data='forward'))
            if transfer(a)!='':
                markup.add(types.InlineKeyboardButton(text='🔄 '+LINES[transfer(a)], callback_data='transfer'))
            markup.add(types.InlineKeyboardButton(text='🏛 Выйти в город', callback_data='city'))
            map = 'https://telegra.ph/file/d8e0fbd1a975625a86713.jpg'
            if line!=2 and line!=0:
                msg = await main.send_photo(call.message.chat.id, map, caption='<i>Станция <b>{0}</b>\n{1}</i>'.format(station, desc), parse_mode = 'html', reply_markup = markup)
            else:
                msg = await main.send_photo(call.message.chat.id, map, caption='<i>Остановочный пункт <b>{0}</b>\n{1}</i>'.format(station, desc), parse_mode = 'html', reply_markup = markup)
            await asyncio.sleep(ticket_time)
            try:
                await main.delete_message(call.message.chat.id, msg['message_id'])
            except:
                pass
        except Exception as e:
            await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    async def tostation(user, station, line=100):
        a = user
        if line == 100:
            cursor.execute('SELECT line FROM userdata WHERE user_id=?', (a,))
            lines = cursor.fetchone()[0]
        else:
            lines = line
        cursor.execute('UPDATE userdata SET place = ? WHERE user_id=?', (station, a,))
        conn.commit()
        cursor.execute('UPDATE userdata SET line = ? WHERE user_id=?', (lines, a,))
        conn.commit()
    def transfer(user):
        a = user
        cursor.execute('SELECT line FROM userdata WHERE user_id = ?', (a,))
        line = cursor.fetchone()[0]
        cursor.execute('SELECT place FROM userdata WHERE user_id = ?', (a,))
        station = cursor.fetchone()[0]
        for i in range(0,4):
            if i!=line and station in metro[i]:
                return i
        return ''
    async def setrasa(message, user, rasa, photo):
        photos = ['https://te.legra.ph/file/e088cc301adede07db382.jpg', 'https://te.legra.ph/file/ae98cd7c2cad60f6fdcd1.jpg', 'https://te.legra.ph/file/3f3cbfb04a7d1c39bb849.jpg', 'https://te.legra.ph/file/debe702d527967f9afd9a.jpg', 'https://te.legra.ph/file/5a07905d42444f2294418.jpg']
        try:
            a = user.id
            cursor.execute('UPDATE userdata SET rase = ? WHERE user_id = ?', (rasa, a,))
            conn.commit()
            cursor.execute('UPDATE userdata SET  = ? WHERE user_id = ?', (rasa, a,))
            conn.commit()
            cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
            ras = cursor.fetchone()[0]
            await main.send_photo(message.chat.id, photos[photo], caption='<i>Ваша раса: <b>{0}</b></i>'.format(ras), parse_mode = 'html')
        except Exception as e:
            await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    @bot.message_handler(content_types=['text'])
    async def get_text_messages(message: types.Message):
        try:
            a = message.from_user.id
            chid = message.chat.id
            user = message.from_user
            cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (message.chat.id,))
            count = cursor.fetchone()[0]
            if count != 0:
                cursor.execute("SELECT mat FROM clandata WHERE group_id=?", (message.chat.id,))
                mat = cursor.fetchone()[0]
                if mat == 0:
                    for WORD in message.text.lower().split(' '):
                        if WORD.replace(',', '').replace(' ', '') in badwords:
                            await main.delete_message(message.chat.id, message.message_id)
                            return
            await check(message.from_user.id, message.chat.id)
            if message.from_user.is_bot:
                return
            try:
                cursor.execute('SELECT process FROM userdata WHERE user_id=?', (a,))
                process = cursor.fetchone()[0]
            except:
                if message.chat.type=='private' and message.text.lower()!=createacc:
                    process = 'login'
                else:
                    process = ''
            if process=='login':
                key = message.text
                cursor.execute('SELECT COUNT(*) FROM userdata WHERE user_id=?', (a,))
                count = cursor.fetchone()[0]
                if count>0:
                    cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                    conn.commit()
                    await main.send_message(chid, '<i>Кажется, вы уже зарегистрированы в Живополисе. Сначала выйдите из аккаунта</i>', parse_mode='html')
                    return
                cursor.execute('SELECT COUNT(*) FROM userdata WHERE accesskey=? AND user_id=0', (key,))
                count = cursor.fetchone()[0]
                if count!=1:
                    cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                    conn.commit()
                    await main.send_message(chid, '<i>Кажется, вы ввели неправильный ключ</i>', parse_mode='html')
                    return
                cursor.execute('UPDATE userdata SET user_id=? WHERE accesskey=?', (a,key,))
                conn.commit()
                cursor.execute('UPDATE userdata SET user_name=? WHERE accesskey=?', (user.first_name,key,))
                conn.commit()
                cursor.execute('UPDATE userdata SET user_surname=? WHERE accesskey=?', (user.last_name,key,))
                conn.commit()
                cursor.execute('UPDATE userdata SET username=? WHERE accesskey=?', (user.username,key,))
                conn.commit()
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
                await main.send_message(fid, '<i><b><a href="tg://user?id={0}">{1}</a></b> вошёл(-а) в аккаунт Живополиса\n#user_login</i>'.format(user.id, user.first_name), parse_mode='html')
                await startdef(message)
            if process=='setkey':
                if message.chat.type!='private':
                    await main.send_message(chid, '<i>В целях обеспечения конфиденциальности пользователей эта команда работает только в личных сообщениях с ботом. Откройте настройки в ЛС с ботом и заново введите ключ доступа</i>', parse_mode='html')
                    cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                    conn.commit()
                    return
                chid = message.chat.id
                a = message.from_user.id
                key = message.text
                cursor.execute('SELECT COUNT(*) FROM userdata WHERE accesskey=?', (key,))
                count = cursor.fetchone()[0]
                if count!=0:
                    await main.send_message(chid, '<i>Такой ключ уже зарегистрирован</i>', parse_mode='html')
                    return
                cursor.execute('UPDATE userdata SET accesskey = ? WHERE user_id = ?', (message.text, a,))
                conn.commit()
                cursor.execute('SELECT accesskey FROM userdata WHERE user_id = ?', (a,))
                desc = cursor.fetchone()[0]
                await message.answer('<i>Ваш ключ доступа: \n<b>{0}</b></i>'.format(desc), parse_mode = 'html')
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
            if process=='seekhouse':
                if message.chat.type=='private':
                    a = message.from_user.id
                    house = int(message.text)
                    cursor.execute('SELECT place FROM userdata WHERE user_id = ?', (a,))
                    place = cursor.fetchone()[0]
                    clans = ''
                    cursor.execute('SELECT count(*) FROM clandata WHERE hqplace = ? AND type=? AND address=?', (place, 'public', house,))
                    count = cursor.fetchone()[0]
                    if count == 0:
                        await message.answer('<i>Кланов не найдено :(</i>', parse_mode = 'html')
                        cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                        conn.commit()
                        return
                    cursor.execute('SELECT * FROM clandata WHERE hqplace = ? AND type = ? AND address=? ORDER BY address LIMIT 25', (place, 'public', house,))
                    for row in cursor:
                        clans+='\n<a href = "{0}">{1}</a>'.format(row[8], row[1])
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='Искать по номеру дома', callback_data='hq_number'))
                    await message.answer('<i>&#127970; Найденные кланы: <b>{0}</b></i>'.format(clans), parse_mode = 'html', reply_markup=markup)
                    cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                    conn.commit()
            if process=='setbio':
                a = message.from_user.id
                cursor.execute('UPDATE userdata SET desc = ? WHERE user_id = ?', (message.text, a,))
                conn.commit()
                cursor.execute('SELECT desc FROM userdata WHERE user_id = ?', (a,))
                desc = cursor.fetchone()[0]
                await message.answer('<i>Ваше описание: \n<b>{0}</b></i>'.format(desc), parse_mode = 'html')
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
            if process=='setnick':
                a = message.from_user.id
                cursor.execute('UPDATE userdata SET nick = ? WHERE user_id = ?', (message.text, a,))
                conn.commit()
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
                nick = cursor.fetchone()[0]
                await message.answer('<i>Ваш ник: <b>{0}</b></i>'.format(nick), parse_mode = 'html')
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
            if process=='setphoto':
                a = message.from_user.id
                cursor.execute('UPDATE userdata SET photo = ? WHERE user_id = ?', (message.text, a,))
                conn.commit()
                cursor.execute('SELECT photo FROM userdata WHERE user_id = ?', (a,))
                photo = cursor.fetchone()[0]
                try:
                    await main.send_photo(message.chat.id, photo, caption = '<i>Ваше фото</i>', parse_mode = 'html')
                except:
                    await message.answer('<i>Произошла ошибка при публикации фото. Фото профиля удалено</i>', parse_mode = 'html')
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
            if process=='clanname':
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
                    return
                cursor.execute('UPDATE clandata SET name=? WHERE group_id=?', (message.text, chid,))
                conn.commit()
                cursor.execute('SELECT name FROM clandata WHERE group_id=?', (chid,))
                name = cursor.fetchone()[0]
                await main.send_message(chid, '<i>Новое название клана: <b>{0}</b></i>'.format(name), parse_mode = 'html')
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
            if process=='clanbio':
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
                    return
                cursor.execute('UPDATE clandata SET bio=? WHERE group_id=?', (message.text, chid,))
                conn.commit()
                cursor.execute('SELECT bio FROM clandata WHERE group_id=?', (chid,))
                bio = cursor.fetchone()[0]
                await main.send_message(chid, '<i>Новое описание клана: <b>{0}</b></i>'.format(bio), parse_mode = 'html')
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
            if process=='clanphoto':
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
                    return
                cursor.execute('UPDATE clandata SET photo=? WHERE group_id=?', (message.text, chid,))
                conn.commit()
                cursor.execute('SELECT photo FROM clandata WHERE group_id=?', (chid,))
                photo = cursor.fetchone()[0]
                try:
                    await main.send_photo(message.chat.id, photo, caption = '<i>Фото клана</i>', parse_mode = 'html')
                except:
                    await message.answer('<i>Произошла ошибка при публикации фото. Фото клана удалено</i>', parse_mode = 'html')
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
            if process=='clanuser':
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
                    return
                cursor.execute('UPDATE clandata SET username=? WHERE group_id=?', (message.text, chid,))
                conn.commit()
                cursor.execute('SELECT name FROM clandata WHERE group_id=?', (chid,))
                name = cursor.fetchone()[0]
                await startdef(message)
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
        except Exception as e:
            if 'invalid literal' in str(e):
                await main.send_message(chid, '&#10060; <i><b>Ошибка:</b> Введите целое число</i>', parse_mode='html')
            else:
                await main.send_message(chid, '&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await main.send_message(chid, '<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if message.text.lower().startswith('живополис, '):
            text = message.text.lower()[11:]
            if text.startswith('привет'):
                await message.reply('<i>{0}</i>'.format(random.choice(['Да-да, привет', 'Здравствуй', 'Здравия желаю', 'Вечер в хату', 'Ну привет!'])), parse_mode='html')
            elif text.startswith('как дела'):
                await message.reply('<i>{0}</i>'.format(random.choice(['Нормально', 'Нормально. А у тебя?', 'Типа того', 'Норм', 'Ну, нормас типа'])), parse_mode='html')
            elif 'или' in text:
                await message.reply('<i>{0}</i>'.format(random.choice(text.split(' или '))), parse_mode='html')
            else:
                await message.reply('<i>{0}</i>'.format(random.choice(['А?', 'Что надо?', 'Чё звал?', 'Ещё раз позовёшь - получишь бан!', 'И тебе привет', 'Да?'])), parse_mode='html')
        if message.text.lower() == createacc:
            await create_acc(message.from_user, message.chat.id)
        if message.text.lower() == '/id':
            if hasattr(message.reply_to_message, "text"):
                await message.reply('{0.id}'.format(message.reply_to_message.from_user))
            else:
                await message.reply('{0.id}'.format(message.from_user))
        if message.text.lower() == 'хто я':
            await message.reply('Ты даун' if message.from_user.id == 1002930622 else 'Ты {0.first_name}'.format(message.from_user))
        if message.text.lower() == 'ахах':
            await message.reply('Разрывная')
        if message.text.lower() == 'ид':
            try:
                a = message.from_user.id
                cursor.execute('SELECT user_id FROM userdata WHERE user_id=?', (a,))
                for ids in cursor.fetchall():
                    await message.answer(ids)
            except Exception as e:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if message.text.lower() == 'мой баланс':
            try:
                a = message.from_user.id
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                money = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                await message.answer('<i><b><a href="tg://user?id={1}">{3}{0}</a></b> размахивает перед всеми своими накоплениями в количестве <b>${2}</b></i>'.format(nick, a, money, rasa), parse_mode = 'html')
            except Exception as e:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if message.text.startswith('$='):
            try:
                a = message.from_user.id
                cursor.execute('SELECT rang FROM userdata WHERE user_id=?', (a,))
                rang = cursor.fetchone()[0]
                if rang<2:
                    await message.answer('&#10060; <i>Эта команда доступна только с ранга <b>[2] Админ</b></i>', parse_mode='html')
                    return
                cursor.execute('UPDATE userdata SET balance = ? WHERE user_id = ?', (int(message.text[2:]), message.from_user.id,))
                conn.commit()
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                await message.answer('Ваш баланс: {0}'.format(cursor.fetchone()[0]))
            except Exception as e:
                await message.answer('&#10060; <i><b>Ошибка:</b> {0}</i>'.format(e), parse_mode='html')
        if message.text.lower()=='вылечить':
            if not hasattr(message.reply_to_message, 'text'):
                await message.answer('<i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
            else:
                await cure(message.from_user.id, message.reply_to_message.from_user.id, message.chat.id)
        if message.text.lower()=='отравить':
            if not hasattr(message.reply_to_message, 'text'):
                await message.answer('<i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
            else:
                await poison(message.from_user.id, message.reply_to_message.from_user.id, message.chat.id)
        if message.text.lower()=='выстрел':
            if not hasattr(message.reply_to_message, 'text'):
                await message.answer('<i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
            else:
                await shoot(message.from_user.id, message.reply_to_message.from_user.id, message.chat.id)
        if message.text.lower().startswith('/ban '):
            try:
                arr = message.text.split(" ", maxsplit=2)
                a = message.from_user.id
                cursor.execute('SELECT rang FROM userdata WHERE user_id=?', (a,))
                rang = cursor.fetchone()[0]
                if rang<2:
                    await message.answer('&#10060; <i>Эта команда доступна только с ранга <b>[2] Админ</b></i>', parse_mode='html')
                    return
                cursor.execute('SELECT typeof({0}) FROM userdata'.format(arr[1]))
                typ = cursor.fetchone()[0]
                if typ=='text':
                    cursor.execute('UPDATE userdata SET {0} = ? WHERE user_id = ?'.format(arr[1]), (arr[2], a,))
                else:
                    cursor.execute('UPDATE userdata SET {0} = ? WHERE user_id = ?'.format(arr[1]), (int(arr[2]), a,))
                conn.commit()
                cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(arr[1]), (a,))
                await message.answer('Результат: {0}'.format(cursor.fetchone()[0]))
            except Exception as e:
                await message.answer('&#10060; <i><b>Ошибка:</b> {0}</i>'.format(e), parse_mode='html')
        if message.text.lower().startswith('/update '):
            try:
                arr = message.text.split(" ", maxsplit=3)
                cursor.execute('SELECT rang FROM userdata WHERE user_id=?', (a,))
                rang = cursor.fetchone()[0]
                cursor.execute('SELECT rang FROM userdata WHERE user_id=?', (arr[1],))
                orang = cursor.fetchone()[0]
                cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(arr[2]), (arr[1],))
                val = cursor.fetchone()[0]
                if int(arr[1]) == 1006534370 and message.from_user.id!=1006534370 and (rang!=3 and arr[2]!='rang'):
                    await message.answer('&#10060; <i>СЛЫШЬ, ЗАХОТЕЛ ИМПЕРАТОРУ ИНВЕНТАРЬ ОБНУЛИТЬ, ПИДАРАЗ?</i>', parse_mode='html')
                    return
                if arr[2]=='desc' or arr[2]=='nick' or arr[2]=='user_id' or (arr[2] == 'rasa' and orang>=2):
                    await message.answer('&#10060; <i>СЛЫШЬ, ЭТО МЕНЯТЬ НЕЛЬЗЯ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!</i>', parse_mode='html')
                    return
                a = message.from_user.id
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                if rang<2:
                    await message.answer('&#10060; <i>Эта команда доступна только с ранга <b>[2] Админ</b></i>', parse_mode='html')
                    return
                cursor.execute('SELECT typeof({0}) FROM userdata'.format(arr[2]))
                typ = cursor.fetchone()[0]
                if typ=='text':
                    cursor.execute('UPDATE userdata SET {0} = ? WHERE user_id = ?'.format(arr[2]), (arr[3], int(arr[1]),))
                else:
                    cursor.execute('UPDATE userdata SET {0} = ? WHERE user_id = ?'.format(arr[2]), (int(arr[3]), int(arr[1]),))
                conn.commit()
                cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(arr[2]), (arr[1],))
                await message.answer('<i>Результат: <b>{0}</b></i>'.format(cursor.fetchone()[0]), parse_mode = 'html')
                cursor.execute("SELECT COUNT(*) FROM userdata WHERE user_id=?", (arr[1],))
                count = cursor.fetchone()[0]
                if count == 1:
                    cursor.execute("SELECT rasa FROM userdata WHERE user_id=?", (arr[1],))
                    orasa = cursor.fetchone()[0]
                    cursor.execute("SELECT nick FROM userdata WHERE user_id=?", (arr[1],))
                    onick = cursor.fetchone()[0]
                    ouser = "<a href='tg://user?id={0}'>{1}{2}</a>".format(arr[1], orasa, onick)
                else:
                    ouser = "не определён"
                await main.send_message(fid, "<i><b><a href='tg://user?id={0}'>{1}{2}</a></b> выполнил команду:\n\n<code>{3}</code>\n\nПользователь: <b>{4}</b>\nПервоначальное значение: <b>{5}</b>\n#admin_update</i>".format(a, rasa, nick, message.text.lower(), ouser, val), parse_mode = 'html')
            except Exception as e:
                await message.answer('&#10060; <i><b>Ошибка:</b> {0}</i>'.format(e), parse_mode='html')
        if message.text.lower().startswith('/broadcast '):
            try:
                text = message.text[11:]
                a = message.from_user.id
                cursor.execute('SELECT rang FROM userdata WHERE user_id=?', (a,))
                rang = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                if rang<2:
                    await message.answer('&#10060; <i>Эта команда доступна только с ранга <b>[2] Админ</b></i>', parse_mode='html')
                    return
                cursor.execute('SELECT user_id FROM userdata')
                k=0
                ke=0
                for usid in cursor.fetchall():
                    try:
                        await main.send_message(usid[0], '<i><b>Официальное сообщение\n<b>Отправитель:</b> <a href="tg://user?id={0}">{1}{2}</a></b> ({4})\n\n{3}</i>'.format(a, rasa, nick, text, message.from_user.first_name), parse_mode='html')
                        k+=1
                    except Exception as e:
                        ke+=1
                await main.send_message(a, '<i>&#128227; <b>Рассылка по пользователям завершена</b>\n&#9989; Доставлено: {0}\n&#10060; Ошибки: {1}</i>'.format(k, ke), parse_mode='html')
                cursor.execute('SELECT group_id FROM clandata WHERE notif=1')
                k=0
                ke=0
                for usid in cursor.fetchall():
                    try:
                        await main.send_message(usid[0], '<i><b>Официальное сообщение\n<b>Отправитель:</b> <a href="tg://user?id={0}">{1}{2}</a></b> ({4})\n\n{3}</i>'.format(a, rasa, nick, text, message.from_user.first_name), parse_mode='html')
                        k+=1
                    except Exception as e:
                        ke+=1
                await main.send_message(a, '<i>&#128227; <b>Рассылка по кланам завершена</b>\n&#9989; Доставлено: {0}\n&#10060; Ошибки: {1}</i>'.format(k, ke), parse_mode='html')
            except Exception as e:
                await message.answer('&#10060; <i><b>Ошибка:</b> {0}</i>'.format(e), parse_mode='html')
        if message.text.lower().startswith('/select '):
            try:
                arr = message.text.lower().split(" ")
                a = message.from_user.id
                cursor.execute('SELECT rang FROM userdata WHERE user_id=?', (a,))
                rang = cursor.fetchone()[0]
                if rang<2:
                    await message.answer('&#10060; <i>Эта команда доступна только с ранга <b>[2] Админ</b></i>', parse_mode='html')
                    return
                cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(arr[2]), (arr[1],))
                await message.answer('Результат: {0}'.format(cursor.fetchone()[0]))
            except Exception as e:
                await message.answer('&#10060; <i><b>Ошибка:</b> {0}</i>'.format(e), parse_mode='html')
        if message.text.lower().startswith('чек '):
            try:
                a = message.from_user.id
                try:
                    money = int(message.text[4:])
                except:
                    try:
                        money = float(message.text[4:])
                    except:
                        return
                    else:
                        await message.answer('&#10060; <i><b>Ошибка:</b> Введите целое число</i>', parse_mode='html')
                    return
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                if money<=0:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='💵 Оплатить счёт', callback_data='paybill {0} {1}'.format(-money, a)))
                    await message.answer('<i>&#128181; <b><a href="tg://user?id={3}">{0}{1}</a></b> выставил вам счёт на сумму <b>${2}</b></i>'.format(rasa, nick, -money, a), parse_mode='html', reply_markup = markup)
                    if money<0:
                        await main.send_message(fid, '<i>&#128178; <b><a href="tg://user?id={3}">{0}{1}</a></b> выставил счёт на <b>${2}</b>\n#user_check</i>'.format(rasa, nick, -money, a), parse_mode='html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance>=money:
                    cursor.execute('UPDATE userdata SET balance = ? WHERE user_id=?', (balance-money, a,))
                    conn.commit()
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='💲 Забрать деньги', callback_data='check_{0}'.format(money)))
                    await message.answer('<i>&#128178; <b><a href="tg://user?id={3}">{0}{1}</a></b> предлагает вам <b>${2}</b></i>'.format(rasa, nick, money, a), parse_mode='html', reply_markup = markup)
                    if money>0:
                        await main.send_message(fid, '<i>&#128178; <b><a href="tg://user?id={3}">{0}{1}</a></b> выписал чек на <b>${2}</b>\n#user_bill</i>'.format(rasa, nick, money, a), parse_mode='html')
                else:
                    await message.answer('&#10060; <i>У вас недостаточно денег</i>', parse_mode='html')
                try:
                    await main.delete_message(message.chat.id, message.message_id)
                except:
                    pass
            except Exception as e:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if message.text.lower().startswith('продать '):
            try:
                a = message.from_user.id
                arr = message.text.lower().split(' ')
                item = arr[1]
                if not item in items[0]:
                    await message.answer('&#10060; <i>Такого предмета нет в Живополисе</i>', parse_mode='html')
                    return
                else:
                    temp = item
                    ind = items[0].index(temp)
                    item = items[1][ind]
                    itm = temp+' '+items[2][ind]
                try:
                    cost = int(arr[2])
                except:
                    cost = 0
                if cost<0:
                    await message.reply('&#10060; <i>Слоты так не работают</i>', parse_mode='html')
                    return
                cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(item), (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                if balance>=1:
                    cursor.execute('UPDATE userdata SET {0} = ? WHERE user_id=?'.format(item), (balance-1, a,))
                    conn.commit()
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='Купить за ${0}'.format(cost), callback_data='slot {0} {1} {2}'.format(item, cost, a)))
                    await message.answer('<i><b><a href="tg://user?id={3}">{0}{1}</a></b> предлагает вам <b>{4}</b> за <b>${2}</b></i>'.format(rasa, nick, cost, a, itm), parse_mode='html', reply_markup = markup)
                    if cost>0:
                        await main.send_message(fid, '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> продаёт <b>{4}</b> за <b>${2}</b>\n#user_sellitem</i>'.format(rasa, nick, cost, a, itm), parse_mode='html')
                else:
                    await message.answer('&#10060; <i>У вас недостаточно единиц данного предмета</i>', parse_mode='html')
                try:
                    await main.delete_message(message.chat.id, message.message_id)
                except:
                    pass
            except Exception as e:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if message.text.lower().startswith('передать ') or message.text.lower().startswith('пожертвовать '):
            try:
                a = message.from_user.id
                chid = message.chat.id
                if hasattr(message.reply_to_message, 'text'):
                    if message.text.lower().startswith('передать '):
                        amount = int(message.text[9:])
                    else:
                        amount = int(message.text[13:])
                    cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                    mymoney = cursor.fetchone()[0]
                    a = message.reply_to_message.from_user.id
                    cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                    othmoney = cursor.fetchone()[0]
                    if mymoney >= amount:
                        if amount >= 0:
                            cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                            nick = cursor.fetchone()[0]
                            cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                            rasa = cursor.fetchone()[0]
                            if message.from_user.id == message.reply_to_message.from_user.id:
                                await main.send_message(chid, '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> перекладывает из кармана в карман <b>${2}</b></i>'.format(rasa, nick, amount, message.from_user.id), parse_mode='html')
                                return
                            cursor.execute('UPDATE userdata SET balance = ? where user_id = ?', (mymoney - amount, message.from_user.id))
                            cursor.execute('UPDATE userdata SET balance = ? where user_id = ?', (othmoney + amount, message.reply_to_message.from_user.id))
                            conn.commit()
                            a = message.from_user.id
                            cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                            mymoney = cursor.fetchone()[0]
                            oth = message.reply_to_message.from_user.id
                            cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (oth,))
                            othmoney = cursor.fetchone()[0]
                            cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                            nick = cursor.fetchone()[0]
                            cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                            rasa = cursor.fetchone()[0]
                            cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (oth,))
                            onick = cursor.fetchone()[0]
                            cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (oth,))
                            orasa = cursor.fetchone()[0]
                            await message.answer('<i><b><a href="tg://user?id={2}">{0}{1}</a></b> передал <b><a href="tg://user?id={3}">{4}{5}</a></b> ${6}</i>'.format(rasa, nick, a, oth, orasa, onick, amount), parse_mode = 'html')
                            if amount>0:
                               await main.send_message(fid, '<i><b><a href="tg://user?id={2}">{0}{1}</a></b> передал <b><a href="tg://user?id={3}">{4}{5}</a></b> ${6}\n#user_moneyshare</i>'.format(rasa, nick, a, oth, orasa, onick, amount), parse_mode = 'html')
                        else:
                            await message.answer('<i>Введите неотрицательное число</i>', parse_mode='html')
                    else:
                        await message.answer('<i>У вас недостаточно денег</i>', parse_mode='html')
                else:
                    if message.chat.type == 'private':
                        return
                    if message.text.lower().startswith('передать '):
                        amount = int(message.text[9:])
                    else:
                        amount = int(message.text[13:])
                    cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                    count = cursor.fetchone()[0]
                    if count == 0:
                        await startdef(message)
                        return
                    cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                    mymoney = cursor.fetchone()[0]
                    cursor.execute('SELECT balance FROM clandata WHERE group_id=?', (chid,))
                    othmoney = cursor.fetchone()[0]
                    if mymoney >= amount:
                        if amount >= 0:
                            cursor.execute('UPDATE userdata SET balance = ? where user_id = ?', (mymoney - amount, message.from_user.id))
                            cursor.execute('UPDATE clandata SET balance = ? where group_id = ?', (othmoney + amount, chid))
                            conn.commit()
                            cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                            mymoney = cursor.fetchone()[0]
                            cursor.execute('SELECT balance FROM clandata WHERE group_id=?', (chid,))
                            othmoney = cursor.fetchone()[0]
                            cursor.execute('SELECT name FROM clandata WHERE group_id=?', (chid,))
                            chn = cursor.fetchone()[0]
                            cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                            nick = cursor.fetchone()[0]
                            cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                            rasa = cursor.fetchone()[0]
                            await message.answer('<i><b><a href="tg://user?id={2}">{0}{1}</a></b> пожертвовал на нужды клана <b>${3}</b>. Теперь баланс клана: <b>${4}</b></i>'.format(rasa, nick, a, amount, othmoney), parse_mode = 'html')
                            if amount>0:
                                await main.send_message(fid, '<i><b><a href="tg://user?id={2}">{0}{1}</a></b> пожертвовал на нужды клана <b>${3}</b>. Теперь баланс клана <b>{5} ({6})</b>: <b>${4}</b>\n#clan_moneyshare</i>'.format(rasa, nick, a, amount, othmoney, chn, chid), parse_mode = 'html')
                        else:
                            await message.answer('<i>Введите неотрицательное число</i>', parse_mode='html')
                    else:
                        await message.answer('<i>У вас недостаточно денег</i>', parse_mode='html')
            except ValueError:
                return
            except OverflowError:
                await message.answer('&#10060; <i><b>Ошибка:</b> Чересчур большое значение</i>', parse_mode='html')
            except TypeError:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
        if message.text.lower().startswith('отдать '):
            try:
                a = message.from_user.id
                if not hasattr(message.reply_to_message, 'text'):
                    await message.answer('&#10060; <i>Необходимо ответить на сообщение пользователя</i>', parse_mode='html')
                    return
                oth = message.reply_to_message.from_user.id
                arr = message.text.lower().split(' ')
                if a == oth:
                    await message.answer('&#10060; <i>Нельзя передавать предметы самому себе</i>', parse_mode='html')
                    return
                if len(arr)>=3:
                    amount = abs(int(arr[2]))
                else:
                    amount = 1
                item = arr[1]
                if not item in items[0]:
                    await message.answer('&#10060; <i>Такого предмета нет в Живополисе</i>', parse_mode='html')
                    return
                index = items[0].index(item)
                item = items[1][index]
                cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(item), (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(item), (oth,))
                obalance = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (oth,))
                onick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (oth,))
                orasa = cursor.fetchone()[0]
                if balance<amount:
                    await message.answer('&#10060; <i>У вас недостаточно единиц данного предмета</i>', parse_mode='html')
                    return
                cursor.execute('UPDATE userdata SET {0} = ? WHERE user_id=?'.format(item), (balance-amount, a))
                cursor.execute('UPDATE userdata SET {0} = ? WHERE user_id=?'.format(item), (obalance+amount, oth))
                conn.commit()
                await message.answer('<i>&#9989; Передача прошла успешно</i>', parse_mode='html')
                if amount>0:
                    await main.send_message(fid, '<i><b><a href="tg://user?id={0}">{1}{2}</a></b> передал <b><a href="tg://user?id={3}">{4}{5}</a></b> <b>{6} {7}</b>\n#user_itemshare</i>'.format(a, rasa, nick, oth, orasa, onick, amount, '{0} {1}'.format(ITEMS[0][ITEMS[1].index(item)], ITEMS[2][ITEMS[1].index(item)])), parse_mode='html')
            except Exception as e:
                await message.answer('&#10060; <i><b>Ошибка:</b> {0}</i>'.format(e), parse_mode='html')
        if message.text.lower().startswith('вывести '):
            try:
                a = message.from_user.id
                chid = message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    await startdef(message)
                    return
                amount = int(message.text[8:])
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Выводить деньги из клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                mymoney = cursor.fetchone()[0]
                cursor.execute('SELECT balance FROM clandata WHERE group_id=?', (chid,))
                othmoney = cursor.fetchone()[0]
                if othmoney >= 2*amount:
                    if amount >= 0:
                        cursor.execute('UPDATE userdata SET balance = ? where user_id = ?', (mymoney+amount, message.from_user.id))
                        cursor.execute('UPDATE clandata SET balance = ? where group_id = ?', (othmoney-amount, chid))
                        conn.commit()
                        cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                        mymoney = cursor.fetchone()[0]
                        cursor.execute('SELECT balance FROM clandata WHERE group_id=?', (chid,))
                        othmoney = cursor.fetchone()[0]
                        cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                        nick = cursor.fetchone()[0]
                        cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                        rasa = cursor.fetchone()[0]
                        await message.answer('<i><b><a href="tg://user?id={2}">{0}{1}</a></b> вывел из клана <b>${3}</b>. Теперь баланс клана: <b>${4}</b></i>'.format(rasa, nick, a, amount, othmoney), parse_mode = 'html')
                        cursor.execute('SELECT name FROM clandata WHERE group_id=?', (chid,))
                        chn = cursor.fetchone()[0]
                        if amount>0:
                            await main.send_message(fid, '<i><b><a href="tg://user?id={2}">{0}{1}</a></b> вывел из клана <b>{5} ({6})</b> деньги суммой <b>${3}</b>. Теперь баланс клана: <b>${4}</b>\n#clan_moneytake</i>'.format(rasa, nick, a, amount, othmoney, chn, chid), parse_mode = 'html')
                    else:
                        await message.answer('<i>Введите неотрицательное число</i>', parse_mode='html')
                else:
                    await message.answer('<i>Нельзя вывести больше половины баланса клана за раз</i>', parse_mode='html')
            except ValueError:
                return
            except OverflowError:
                await message.answer('&#10060; <i><b>Ошибка:</b> Чересчур большое значение</i>', parse_mode='html')
            except TypeError:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
        if message.text.lower() == 'украсть' or message.text.lower() == 'обворовать':
            try:
                amount = random.randint(1, 10)
                situation = random.uniform(0,1)
                if message.from_user.id == message.reply_to_message.from_user.id:
                    await message.answer('<i>&#10060; Нельзя воровать у самого себя</i>', parse_mode = 'html')
                    return
                a = message.from_user.id
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                mymoney = cursor.fetchone()[0]
                a = message.reply_to_message.from_user.id
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                othmoney = cursor.fetchone()[0]
                cursor.execute('SELECT rang FROM userdata WHERE user_id=?', (a,))
                rang = cursor.fetchone()[0]
                if rang >= 1:
                    await message.answer('<i>&#10060; У администраторов Живополиса и VIP-пользователей воровать нельзя!</i>', parse_mode = 'html')
                    return
                myid = message.from_user.id
                now = datetime.now()
                cursor.execute('SELECT cansteal FROM userdata WHERE user_id=?', (myid,))
                steal = cursor.fetchone()[0]
                diff = (now - datetime.fromtimestamp(0)).total_seconds() - steal
                if diff >= 180:
                    if situation>=0.75:
                        if othmoney>=amount:
                            cursor.execute('UPDATE userdata SET balance = ? where user_id = ?', (mymoney + amount, message.from_user.id))
                            cursor.execute('UPDATE userdata SET balance = ? where user_id = ?', (othmoney - amount, message.reply_to_message.from_user.id))
                            conn.commit()
                            a = message.from_user.id
                            cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                            mymoney = cursor.fetchone()[0]
                            oth = message.reply_to_message.from_user.id
                            cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (oth,))
                            othmoney = cursor.fetchone()[0]
                            cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                            nick = cursor.fetchone()[0]
                            cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                            rasa = cursor.fetchone()[0]
                            cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (oth,))
                            onick = cursor.fetchone()[0]
                            cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (oth,))
                            orasa = cursor.fetchone()[0]
                            cursor.execute('UPDATE userdata SET cansteal = ? WHERE user_id = ?', ((now - datetime.fromtimestamp(0)).total_seconds(), a,))
                            conn.commit()
                            await message.answer('<i><b><a href="tg://user?id={2}">{0}{1}</a></b> украл у <b><a href="tg://user?id={3}">{4}{5}</a></b> ${6}</i>'.format(rasa, nick, a, oth, orasa, onick, amount), parse_mode = 'html')
                            await main.send_message(fid, '<i><b><a href="tg://user?id={2}">{0}{1}</a></b> украл у <b><a href="tg://user?id={3}">{4}{5}</a></b> ${6}\n#user_stealmoney</i>'.format(rasa, nick, a, oth, orasa, onick, amount), parse_mode = 'html')
                        else:
                            oth = message.reply_to_message.from_user.id
                            cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (oth,))
                            onick = cursor.fetchone()[0]
                            cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (oth,))
                            orasa = cursor.fetchone()[0]
                            await message.answer('<i>У <a href="tg://user?id={2}"><b>{0}{1}</b></a> нет столько денег</i>'.format(orasa, onick, oth), parse_mode = 'html')
                    else:
                        a = message.from_user.id
                        cursor.execute('UPDATE userdata SET cansteal = ? WHERE user_id = ?', ((now - datetime.fromtimestamp(0)).total_seconds(), a,))
                        conn.commit()
                        await message.answer('<i>&#10060; Кража провалилась</i>', parse_mode = 'html')
                else:
                    await message.answer('<i>Воровать можно не чаще, чем раз в 3 минуты</i>', parse_mode = 'html')
            except TypeError:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            except AttributeError:
                await message.answer('&#10060; <i><b>Ошибка:</b> Необходимо ответить на сообщение пользователя</i>', parse_mode='html')
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                await message.answer('&#10060; <i><b>Ошибка:</b> Проблема с базой данных</i>', parse_mode='html')
            except OverflowError:
                await message.answer('&#10060; <i><b>Ошибка:</b> Баланс чересчур большой</i>', parse_mode='html')
        if message.text.lower() == 'пинг':
            await message.reply('Понг', parse_mode = 'html')
        if message.text.lower() == 'профиль':
            if hasattr(message.reply_to_message, 'text'):
                await profile(message.reply_to_message.from_user.id, message)
            else:
                await profile(message.from_user.id, message)
        if message.text.lower().startswith('/nick '):
            try:
                a = message.from_user.id
                cursor.execute('UPDATE userdata SET nick = ? WHERE user_id = ?', (message.text[6:], a,))
                conn.commit()
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
                nick = cursor.fetchone()[0]
                await message.answer('<i>Ваш ник: <b>{0}</b></i>'.format(nick), parse_mode = 'html')
            except Exception as e:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if message.text.lower().startswith('/bio '):
            try:
                a = message.from_user.id
                cursor.execute('UPDATE userdata SET desc = ? WHERE user_id = ?', (message.text[5:], a,))
                conn.commit()
                cursor.execute('SELECT desc FROM userdata WHERE user_id = ?', (a,))
                desc = cursor.fetchone()[0]
                await message.answer('<i>Ваше описание: \n<b>{0}</b></i>'.format(desc), parse_mode = 'html')
            except Exception as e:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if message.text.lower() == 'снять':
            try:
                a = message.from_user.id
                cursor.execute('SELECT mask FROM userdata WHERE user_id=?', (a,))
                mask = cursor.fetchone()[0]
                if mask!='':
                    await putoff(message.from_user.id, message)
                    cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                    await message.answer('<i>Ваша раса: {0}</i>'.format(cursor.fetchone()[0]), parse_mode='html')
                else:
                    await message.answer('&#10060; <i>У вас нет маски</i>', parse_mode='html')
            except Exception as e:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if message.text.lower().startswith('рефка'):
            try:
                a = message.from_user.id
                cursor.execute("SELECT ref FROM userdata WHERE user_id=?", (a,))
                reflink = cursor.fetchone()[0]
                if reflink=='':
                    count = 1
                    while count!=0:
                        symbols = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                        for g in range(0, random.randint(8,10)):
                            reflink+=symbols[random.randint(0, len(symbols)-1)]
                        cursor.execute('SELECT count(user_id) FROM userdata WHERE ref=?', (reflink,))	
                        count = cursor.fetchone()[0]
                    cursor.execute('UPDATE userdata SET ref=? WHERE user_id=?', (reflink, a,))
                    conn.commit()
                style = ''
                color = '0-0-0'
                bgcolor = '255-255-255'
                try:
                    style = message.text.lower()[6:]
                except:
                    style = ''
                if style=='bgbluelight':
                    color = '255-255-255'
                    bgcolor = '0-0-255'
                if style=='bgblue':
                    color = '0-0-0'
                    bgcolor = '0-0-255'
                if style=='bgred':
                    color = '0-0-0'
                    bgcolor = '255-0-0'
                if style=='bggreen':
                    color = '0-0-0'
                    bgcolor='0-255-0'
                if style=='bgyellow':
                    color = '0-0-0'
                    bgcolor = '255-255-0'
                if style=='bgblack':
                    color = '255-255-255'
                    bgcolor = '0-0-0'
                if style=='bgpink':
                    color = '0-0-0'
                    bgcolor = '255-0-255'
                if style=='bgcyan':
                    color = '0-0-0'
                    bgcolor = '0-255-255'
                if style=='red':
                    color = '255-0-0'
                    bgcolor = '255-255-255'
                if style=='blue':
                    color = '0-0-255'
                    bgcolor = '255-255-255'
                if style=='green':
                    color = '0-255-0'
                    bgcolor = '255-255-255'
                if style=='cyan':
                    color = '0-255-255'
                    bgcolor = '255-255-255'
                if style=='pink':
                    color = '255-0-255'
                    bgcolor = '255-255-255'
                if style=='yellow':
                    color = '255-255-0'
                    bgcolor = '0-0-0'
                if style=='yellowlight':
                    color = '255-255-0'
                    bgcolor = '255-255-255'
                ref = 't.me/jivopolisbot?start={0}'.format(reflink)
                await main.send_photo(message.chat.id, "https://api.qrserver.com/v1/create-qr-code/?data={0}&size=512x512&charset-source=UTF-8&charset-target=UTF-8&ecc=L&color={1}&bgcolor={2}&margin=1&qzone=1&format=png".format(ref, color, bgcolor), '<i>Ваша реферальная ссылка: <b>{0}</b></i>'.format(ref), parse_mode = 'html')
            except Exception as e:
                await message.answer('&#10060; <i>Ошибка: {0}</i>'.format(e), parse_mode='html')
        if message.text.lower() == 'бой':
            if not hasattr(message.reply_to_message, 'text'):
                await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                return
            await battle(message, message.from_user.id, message.reply_to_message.from_user.id)
        if message.text.lower() == 'ящик':
            await aschik(message.from_user.id, message)
        if message.text.lower().startswith('/unmute'):
            if not hasattr(message.reply_to_message, 'text'):
                await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                return
            a = message.from_user.id
            oth = message.reply_to_message.from_user.id
            chat = message.chat.id
            thisuser = await main.get_chat_member(chat, a)
            if ((isinstance(await main.get_chat_member(chat, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberAdministrator) and thisuser.can_restrict_members==True) or isinstance(await main.get_chat_member(chat, a), types.ChatMemberOwner)) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberOwner):
                await main.restrict_chat_member(chat, oth, types.ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True, can_send_polls=True, can_invite_users = True, can_pin_messages = True, can_change_info = True))
                await message.reply_to_message.reply('<i>&#128227; Вы снова можете говорить</i>', parse_mode='html')
            else:
                await message.reply('<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
        if message.text.lower().startswith('/promote'):
            if not hasattr(message.reply_to_message, 'text'):
                await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                return
            title = ''
            try:
                title = message.text[9:]
            except:
                title = ''
            a = message.from_user.id
            oth = message.reply_to_message.from_user.id
            chat = message.chat.id
            thisuser = await main.get_chat_member(chat, a)
            if ((isinstance(await main.get_chat_member(chat, a), types.ChatMemberAdministrator) and thisuser.can_promote_members==True) or isinstance(await main.get_chat_member(chat, a), types.ChatMemberOwner)) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberOwner):
                await main.promote_chat_member(chat, oth, is_anonymous=False, can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, can_restrict_members=True, can_promote_members=False, can_change_info=True, can_invite_users=True, can_pin_messages=True)
                if title!='' and (thisuser.custom_title!=None or thisuser.status == 'creator'):
                    try:
                        await main.set_chat_administrator_custom_title(chat, oth, title)
                    except:
                        pass
                await message.reply_to_message.reply('<i>&#128737; Вы стали администратором чата</i>', parse_mode='html')
            else:
                await message.reply('<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
        if message.text.lower().startswith('/demote'):
            if not hasattr(message.reply_to_message, 'text'):
                await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                return
            a = message.from_user.id
            oth = message.reply_to_message.from_user.id
            chat = message.chat.id
            thisuser = await main.get_chat_member(chat, a)
            othuser = await main.get_chat_member(chat, oth)
            if ((isinstance(await main.get_chat_member(chat, a), types.ChatMemberAdministrator) and thisuser.can_promote_members==True and othuser.can_promote_members==False) or isinstance(await main.get_chat_member(chat, a), types.ChatMemberOwner)) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberOwner) and isinstance(await main.get_chat_member(chat, oth), types.ChatMemberAdministrator):
                await main.promote_chat_member(chat, oth, is_anonymous=False, can_manage_chat=False, can_delete_messages=False, can_manage_video_chats=False, can_restrict_members=False, can_promote_members=False, can_change_info=False, can_invite_users=False, can_pin_messages=False)
                await message.reply_to_message.reply('<i>&#128683; Вы перестали быть администратором чата</i>', parse_mode='html')
            else:
                await message.reply('<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
        if message.text.lower().startswith('/mute'):
            if message.text.lower() == '/mute':
                number = 300
                val = 5
                timed = 'минут'
            else:
                try:
                    if message.text.lower()[len(message.text)-1]=='s':
                        val = message.text[5:len(message.text)-1].strip()
                        number = int(val)
                        symbol = message.text.lower()[len(message.text)-1]
                    elif message.text.lower()[len(message.text)-1]=='m':
                        val = message.text[5:len(message.text)-1].strip()
                        number = int(val)*60
                        symbol = message.text.lower()[len(message.text)-1]
                    elif message.text.lower()[len(message.text)-1]=='h':
                        val = message.text[5:len(message.text)-1].strip()
                        number = int(val)*3600
                        symbol = message.text.lower()[len(message.text)-1]
                    elif message.text.lower()[len(message.text)-1]=='d':
                        val = message.text[5:len(message.text)-1].strip()
                        number = int(val)*3600*24
                        symbol = message.text.lower()[len(message.text)-1]
                    elif message.text.lower()[len(message.text)-1]=='w':
                        val = message.text[5:len(message.text)-1].strip()
                        number = int(val)*3600*24*7
                        symbol = message.text.lower()[len(message.text)-1]
                    elif message.text.lower()[len(message.text)-1]=='y':
                        val = message.text[5:len(message.text)-1].strip()
                        number = int(val)*3600*24*365
                        symbol = message.text.lower()[len(message.text)-1]
                    else:
                        val = message.text[5:].strip()
                        number = int(val)
                        symbol = 's'
                    timed = 'секунд'
                    if symbol == 'm':
                        timed = 'минут'
                    if symbol == 'h':
                        timed = 'часов'
                    if symbol == 'd':
                        timed = 'дней'
                    if symbol == 'y':
                        timed = 'лет'
                except Exception as e:
                    await message.answer('&#10060; <i><b>Ошибка:</b> Принимаются только числовые значения</i>', parse_mode='html')
                    await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
                    return
            if not hasattr(message.reply_to_message, 'text'):
                await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                return
            a = message.from_user.id
            oth = message.reply_to_message.from_user.id
            chat = message.chat.id
            thisuser = await main.get_chat_member(chat, a)
            if ((isinstance(await main.get_chat_member(chat, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberAdministrator) and thisuser.can_restrict_members==True) or isinstance(await main.get_chat_member(chat, a), types.ChatMemberOwner)) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberOwner):
                if number<30:
                    await message.answer('&#10060; <i>Минимальное время мута - 30 секунд</i>', parse_mode='html')
                    return
                await main.restrict_chat_member(chat, oth, until_date=time()+number)
                await message.reply_to_message.reply('<i>&#129323; Вы были заглушены на {0} {1}</i>'.format(val, timed), parse_mode='html')
            else:
                await message.reply('<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
        elif message.text.lower()=='рандом бой':
            try:
                chid = message.chat.id
                if message.chat.type=='private':
                    await main.send_message(chid, '<i>Эта команда работает только в чатах</i>', parse_mode='html')
                    return
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    await main.send_message(chid, '<i>Сначала создайте клан</i>', parse_mode='html')
                cursor.execute('SELECT * FROM userdata WHERE clan=? AND ready=1', (chid,))
                nusers = cursor.fetchall()
                cursor.execute('SELECT count(*) FROM userdata WHERE clan=? AND ready=1', (chid,))
                cnt = cursor.fetchone()[0]
                if cnt==0:
                    await main.send_message(chid, '<i>В чате нет готовых к бою игроков :(</i>', parse_mode='html')
                    return
                needed = random.choice(nusers)
                aidy = needed[1]
                nick = needed[7]
                rasa = needed[9]
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='Начать бой', callback_data='battle_{0}'.format(aidy)))
                await main.send_message(chid, '<i>Готов к бою <b><a href="tg://user?id={0}">{1}{2}</a></b></i>'.format(aidy, rasa, nick), parse_mode='html', reply_markup=markup)
            except Exception as e:
                await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if message.text.lower().startswith('/exec '):
            try:
                if message.from_user.id == CREATOR:
                    exec(message.text[6:])
                else:
                    await main.send_message(message.chat.id, '<i>❌ Данная команда доступна только создателю Живополиса</i>', parse_mode='html')
            except Exception as e:
                try:
                    await main.send_message(message.chat.id, '❌ <i><b>Ошибка:</b> {0}</i>'.format(e), parse_mode='html')
                except:
                    await main.send_message(message.chat.id, '❌ Ошибка: {0}'.format(e))
            else:
                await main.send_message(message.chat.id, '<i>✅ Код выполнен без ошибок</i>', parse_mode='html')
        if message.text.lower().startswith('/eval '):
            try:
                if message.from_user.id == CREATOR:
                    res = eval(message.text[6:])
                    await main.send_message(message.chat.id, '<i><b>Результат: </b>{0}</i>'.format(res), parse_mode='html')
                else:
                    await main.send_message(message.chat.id, '<i>❌ Данная команда доступна только создателю Живополиса</i>', parse_mode='html')
            except Exception as e:
                try:
                    await main.send_message(message.chat.id, '❌ <i><b>Ошибка:</b> {0}</i>'.format(e), parse_mode='html')
                except:
                    await main.send_message(message.chat.id, '❌ Ошибка: {0}'.format(e))
        if message.text.lower()=='слава миките слава миките слава миките':
            if message.chat.type!='private':
                return
            try:
                a=message.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                place = cursor.fetchone()[0]
                if place=='Ракенская':
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='Перейти', url='t.me/+zAbW_LMY4ABiZTRi'))
                    await message.answer('<i>Секреееетный чат</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await message.answer('❌ <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    @bot.message_handler(content_types=['document'])
    async def get_document(message: types.Message):
        try:
            await check(message.from_user.id, message.chat.id)
            a = message.from_user.id
            chid = message.chat.id
            user = message.from_user
            try:
                cursor.execute('SELECT process FROM userdata WHERE user_id=?', (a,))
                process = cursor.fetchone()[0]
            except:
                if message.chat.type=='private' and message.text.lower()!=createacc:
                    process = 'login'
                else:
                    process = ''
            if process.startswith('editfile_'):
                path = process.replace('editfile_', '')
                if a!=CREATOR:
                    await message.answer('&#10060; <i>Эта команда доступна только создателю Живополиса</i>', parse_mode='html')
                    return
                await message.document.download(destination_file='text.txt')
                with open('text.txt') as file:
                    text = file.read()
                os.remove('text.txt')
                with open(path, 'r+') as editfile:
                    editfile.write(text)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='♻ Перезагрузка', callback_data = 'restart_bot'))
                markup.add(types.InlineKeyboardButton(text='✅ Готово', callback_data = 'cancel_action'))
                await message.answer('<i>✅ Обновление файла прошло успешно</i>', parse_mode='html', reply_markup = markup)
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
        except Exception as e:
            await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    @bot.message_handler(content_types=['sticker'])
    async def sendst(message: types.Message):
        try:
            if message.from_user.id in banned:
                return
            cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (message.chat.id,))
            count = cursor.fetchone()[0]
            if count != 0:
                cursor.execute("SELECT stickers FROM clandata WHERE group_id=?", (message.chat.id,))
                stickers = cursor.fetchone()[0]
                if stickers == 0:
                    await main.delete_message(message.chat.id, message.message_id)
                    return
            await check(message.from_user.id, message.chat.id)
            a = message.from_user.id
            try:
                cursor.execute("SELECT health FROM userdata WHERE user_id=?", (a,))
                health = cursor.fetchone()[0]
                cursor.execute("SELECT prison FROM userdata WHERE user_id=?", (a,))
                prison = cursor.fetchone()[0]
                if health <= 0 or prison > (datetime.now() - datetime.fromtimestamp(0)).total_seconds():
                    return
            except:
                pass
            cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (message.chat.id,))
            count = cursor.fetchone()[0]
            if count != 0:
                cursor.execute("SELECT stickers FROM clandata WHERE group_id=?", (message.chat.id,))
                stickers = cursor.fetchone()[0]
                if stickers == 0:
                    await main.delete_message(message.chat.id, message.message_id)
                    return
            if '🎲' in message.sticker.emoji:
                if message.chat.id != -1001395868701:
                    message.reply("&#10060; <i>Рулетка не работает за пределами <b>Игрового клуба</b></i>", parse_mode = 'html')
                    return
                try:
                    a = message.from_user.id
                    rand = prizes[random.randint(0,42)]
                    now = datetime.now()
                    cursor.execute('SELECT rulette FROM userdata WHERE user_id = ?', (a,))
                    box = cursor.fetchone()[0]
                    cursor.execute('SELECT morj FROM userdata WHERE user_id = ?', (a,))
                    morj = cursor.fetchone()[0]
                    cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                    balance = cursor.fetchone()[0]
                    diff = (now - datetime.fromtimestamp(0)).total_seconds() - box
                    if diff >= 12*3600:
                        if balance < 10:
                            await message.answer('<i>&#10060; Нельзя играть в рулетку, когда у вас на балансе меньше $10</i>', parse_mode='html')
                            return
                        cursor.execute('UPDATE userdata SET rulette = ? WHERE user_id = ?', ((now - datetime.fromtimestamp(0)).total_seconds(), a,))
                        conn.commit()
                        if rand==0:
                            await message.answer('<i>Вы не получили ничего :(</i>', parse_mode = 'html')
                        elif rand=='morj':
                            await message.answer('<i>Вы получили &#129453; моржа!</i>', parse_mode = 'html')
                            cursor.execute('UPDATE userdata SET morj = ? WHERE user_id = ?', (morj+1, a,))
                            conn.commit()
                        elif rand=='cow':
                            await message.answer('<i>Вы получили &#128004; корову!</i>', parse_mode = 'html')
                            cursor.execute('UPDATE userdata SET cow = ? WHERE user_id = ?', (morj+1, a,))
                            conn.commit()
                        elif rand>0:
                            cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                            balance = cursor.fetchone()[0]
                            cursor.execute('UPDATE userdata SET balance = ? WHERE user_id = ?', (balance+rand, a,))
                            conn.commit()
                            await message.answer('<i><b>Поздравляем!</b>\nВы заработали <b>${0}</b></i>'.format(rand), parse_mode = 'html')
                        else:
                            cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                            balance = cursor.fetchone()[0]
                            cursor.execute('UPDATE userdata SET balance = ? WHERE user_id = ?', (balance+rand, a,))
                            conn.commit()
                            await message.answer('<i>Вы проиграли <b>${0}</b> :(</i>'.format(-rand), parse_mode = 'html')
                    else:
                        h = int(12-ceil(diff/3600))
                        m = int(60-ceil(diff%3600/60))
                        s = int(60-ceil(diff%3600%60))
                        await message.answer('<i>&#10060; Вращать рулетку можно только раз в 12 часов. До следующей попытки осталось {0} часов {1} минут {2} секунд</i>'.format(h,m,s), parse_mode='html')
                except Exception as e:
                    await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                    await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            if '⛔' in message.sticker.emoji:
                try:
                    if not hasattr(message.reply_to_message, 'text'):
                        await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                        return
                    a = message.from_user.id
                    oth = message.reply_to_message.from_user.id
                    chat = message.chat.id
                    thisuser = await main.get_chat_member(chat, a)
                    if (isinstance(await main.get_chat_member(chat, a), types.ChatMemberAdministrator) or isinstance(await main.get_chat_member(chat, a), types.ChatMemberOwner)) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberOwner) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberAdministrator) and thisuser.can_restrict_members==True:
                        await main.restrict_chat_member(chat, oth, until_date=time()+300)
                        await message.reply_to_message.reply('<i>&#129323; Вы были заглушены на 5 минут</i>', parse_mode='html')
                    else:
                        await message.reply('<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
                except Exception as e:
                    await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                    await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            if '⚔' in message.sticker.emoji:
                await battle(message)
            if '🤡' in message.sticker.emoji:
                if not hasattr(message.reply_to_message, 'text'):
                    cursor.execute('SELECT type FROM userdata WHERE user_id=?', (a,))
                    type = cursor.fetchone()[0]
                else:
                    cursor.execute('SELECT type FROM userdata WHERE user_id=?', (message.reply_to_message.from_user.id,))
                    type = cursor.fetchone()[0]
                if type=='private':
                    return
                if hasattr(message.reply_to_message, 'text'):
                    await profile(message.reply_to_message.from_user.id, message)
                else:
                    await profile(message.from_user.id, message)
            if '👑' in message.sticker.emoji:
                if not hasattr(message.reply_to_message, 'text'):
                    await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                    return
                a = message.from_user.id
                oth = message.reply_to_message.from_user.id
                chat = message.chat.id
                thisuser = await main.get_chat_member(chat, a)
                if (isinstance(await main.get_chat_member(chat, a), types.ChatMemberAdministrator) or isinstance(await main.get_chat_member(chat, a), types.ChatMemberOwner)) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberOwner) and thisuser.can_promote_members==True:
                    await main.promote_chat_member(chat, oth, is_anonymous=False, can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, can_restrict_members=True, can_promote_members=False, can_change_info=True, can_invite_users=True, can_pin_messages=True)
                    await message.reply_to_message.reply('<i>&#128737; Вы стали администратором чата</i>', parse_mode='html')
                else:
                    await message.reply('<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
            if '🔥' in message.sticker.emoji:
                if not hasattr(message.reply_to_message, 'text'):
                    await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                    return
                a = message.from_user.id
                oth = message.reply_to_message.from_user.id
                chat = message.chat.id
                thisuser = await main.get_chat_member(chat, a)
                othuser = await main.get_chat_member(chat, oth)
                if (isinstance(await main.get_chat_member(chat, a), types.ChatMemberAdministrator) or isinstance(await main.get_chat_member(chat, a), types.ChatMemberOwner)) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberOwner) and isinstance(await main.get_chat_member(chat, oth), types.ChatMemberAdministrator) and thisuser.can_promote_members==True and othuser.can_promote_members==False:
                    await main.promote_chat_member(chat, oth, is_anonymous=False, can_manage_chat=False, can_delete_messages=False, can_manage_video_chats=False, can_restrict_members=False, can_promote_members=False, can_change_info=False, can_invite_users=False, can_pin_messages=False)
                    await message.reply_to_message.reply('<i>&#128683; Вы перестали быть администратором чата</i>', parse_mode='html')
                else:
                    await message.reply('<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
            if '📣' in message.sticker.emoji:
                try:
                    if not hasattr(message.reply_to_message, 'text'):
                        await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                        return
                    a = message.from_user.id
                    oth = message.reply_to_message.from_user.id
                    chat = message.chat.id
                    thisuser = await main.get_chat_member(chat, a)
                    if (isinstance(await main.get_chat_member(chat, a), types.ChatMemberAdministrator) or isinstance(await main.get_chat_member(chat, a), types.ChatMemberOwner)) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberOwner) and not isinstance(await main.get_chat_member(chat, oth), types.ChatMemberAdministrator) and thisuser.can_restrict_members==True:
                        await main.restrict_chat_member(chat, oth, types.ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_other_messages=True, can_add_web_page_previews=True, can_send_polls=True, can_invite_users = True, can_pin_messages = True, can_change_info = True))
                        await message.reply_to_message.reply('<i>&#128227; Вы снова можете говорить</i>', parse_mode='html')
                    else:
                        await message.reply('<i>&#10060; У вас недостаточно прав</i>', parse_mode='html')
                except Exception as e:
                    await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                    await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            if '💊' in message.sticker.emoji:
                try:
                    if not hasattr(message.reply_to_message, 'text'):
                        await message.answer('&#10060; <i>Нужно ответить на сообщение пользователя</i>', parse_mode='html')
                        return
                    a = message.from_user.id
                    oth = message.reply_to_message.from_user.id
                    chat = message.chat.id
                    await cure(a, oth, chat)
                except Exception as e:
                    await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                    await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            if '🖥' in message.sticker.emoji:
                try:
                    a = message.from_user.id
                    chid = message.chat.id
                    cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                    count = cursor.fetchone()[0]
                    cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
                    rasa = cursor.fetchone()[0]
                    cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
                    nick = cursor.fetchone()[0]
                    cursor.execute("SELECT balance FROM clandata WHERE group_id=?", (chid,))
                    balance = cursor.fetchone()[0]
                    if balance >= 10000:
                        await main.send_message(chid, '<i>&#10060; Нельзя грабить кланы, у которых на балансе больше $10000</i>', parse_mode = 'html')
                        return
                    if count == 0:
                        return
                    rand = random.randint(1,10)
                    if rand<10:
                        cursor.execute('UPDATE userdata SET prison=? WHERE user_id=?', (current_time()+600, a,))
                        conn.commit()
                        await main.send_message(chid, '<i>Видимо, кое-кому придётся немного поучиться взламывать. У вас как раз будет достаточно времени.\n\n&#128110; Господин <b><a href="tg://user?id={0}">{1}{2}</a></b>, вы задержаны за попытку обворовать клан. Пройдёмте в отделение.\n\nВы были арестованы на <b>10 минут</b></i>'.format(a, rasa, nick), parse_mode='html')
                    else:
                        cursor.execute("SELECT balance FROM clandata WHERE group_id=?", (chid,))
                        balance = cursor.fetchone()[0]
                        cursor.execute("SELECT name FROM clandata WHERE group_id=?", (chid,))
                        chn = cursor.fetchone()[0]
                        if balance < 45:
                            await main.send_message(chid, '<i>&#10060; В клане денег почти нет :)</i>', parse_mode = 'html')
                            return
                        rando = random.randint(1, 45)
                        cursor.execute("UPDATE userdata SET balance=balance+? WHERE user_id=?", (rando, a,))
                        conn.commit()
                        cursor.execute("UPDATE clandata SET balance=balance-? WHERE group_id=?", (rando, chid,))
                        conn.commit()
                        await message.answer('<i>&#127942; У вас получилось ограбить клан! Вы унесли с собой <b>${0}</b></i>'.format(rando), parse_mode='html')
                        await main.send_message(fid, '<i><b><a href="tg://user?id={0}">{1}{2}</a></b> взломал клан <b>{3}</b> и унёс с собой <b>${4}</b>\n#clan_hack</i>'.format(a, rasa, nick, chn, rando), parse_mode='html')
                except Exception as e:
                    await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                    await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        except:
            pass
    @bot.message_handler(content_types=['dice'])
    async def dice_value(message: types.Message):
        try:
            if message.from_user.id in banned:
                return
            cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (message.chat.id,))
            count = cursor.fetchone()[0]
            if count != 0:
                cursor.execute("SELECT dice FROM clandata WHERE group_id=?", (message.chat.id,))
                dice = cursor.fetchone()[0]
                if dice == 0:
                    await main.delete_message(message.chat.id, message.message_id)
                    return
            cursor.execute("SELECT count(*) FROM clandata WHERE group_id=?", (message.chat.id,))
            count = cursor.fetchone()[0]
            if count == 0:
                return
            cursor.execute("SELECT gameclub FROM clandata WHERE group_id=?", (message.chat.id,))
            gameclub = cursor.fetchone()[0]
            if gameclub == 1:
                return
            chid = message.chat.id
            if message.forward_date == None:
                a = message.from_user.id
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
                rasa = cursor.fetchone()[0]
                value = message.dice.value
                if message.dice.emoji == '🎰':
                    cursor.execute("SELECT lastplayed FROM userdata WHERE user_id=?", (a,))
                    last = cursor.fetchone()[0]
                    if current_time() - last < 15:
                        await message.reply('<i>❌ Эй, играть можно не более раза в 15 секунд!</i>', parse_mode='html')
                        return
                    if balance>=10:
                        cursor.execute("UPDATE userdata SET lastplayed=? WHERE user_id=?", (current_time(), a,))
                        conn.commit()
                        await message.answer('<i><b><a href="tg://user?id={2}">{0}{1}</a></b> бросает в автомат жетон стоимостью <b>$10</b></i>'.format(rasa, nick, a), parse_mode = 'html')
                        await earn(message, -10)
                        cursor.execute("UPDATE clandata SET balance=balance+5 WHERE group_id=?", (chid,))
                        conn.commit()
                        cursor.execute("UPDATE clandata SET balance=balance+5 WHERE group_id=-1001395868701")
                        conn.commit()
                        cursor.execute("SELECT balance FROM clandata WHERE group_id=?",(chid,))
                        kazbal = cursor.fetchone()[0]
                        cursor.execute("SELECT kazna FROM globaldata")
                        kazna = cursor.fetchone()[0]
                        if value==64:
                            rand = random.randint(225,275)
                            if kazbal>=rand:
                                cursor.execute("UPDATE clandata SET balance=balance-? WHERE group_id=?", (rand, chid,))
                                conn.commit()
                            else:
                                if kazna>=2*rand:
                                    cursor.execute("UPDATE clandata SET balance=balance+? WHERE group_id=-1001395868701", (rand,))
                                    cursor.execute("UPDATE globaldata SET kazna=kazna-?", (2*rand,))
                                    conn.commit()
                                else:
                                    await message.answer('<i>К сожалению, у нас нет денег, чтобы выдать вознаграждение. Приходите позже или пожертвуйте деньги.\nПополнить баланс Игрового клуба можно, набрав сообщение <code>Пожертвовать [сумма]</code>. Пожертвовать деньги в казну можно через Банк</i>'.format(rand), parse_mode = 'html')
                                    return
                            await earn(message,rand)
                            cursor.execute('SELECT jackpots FROM userdata WHERE user_id = ?', (a,))
                            jack = cursor.fetchone()[0]
                            cursor.execute('UPDATE userdata SET jackpots = ? WHERE user_id = ?', (jack+1, a,))
                            conn.commit()
                            cursor.execute('SELECT jackpots FROM userdata WHERE user_id = ?', (a,))
                            jack = cursor.fetchone()[0]
                            await message.answer('<i><b>&#128176; Джекпот!</b>\nВы выигрываете <b>${0}</b>\nВы поймали джекпот всего <b>{1} раз</b></i>'.format(rand, jack), parse_mode = 'html')
                            cursor.execute('SELECT lucky FROM userdata WHERE user_id = ?', (a,))
                            ach = cursor.fetchone()[0]
                            if jack>=10:
                                if ach==0:
                                    await achieve(message.from_user.id, message.chat.id, 'lucky')
                                    await message.answer('<i>Вы получаете <b>&#128477; Ключ</b> от Чёрного рынка. Осталось научиться им пользоваться, и весь мир будет в ваших лапках!</i>', parse_mode = 'html')
                                    cursor.execute('UPDATE userdata SET key=key+1 WHERE user_id=?', (a,))
                                    conn.commit()
                        elif value==43:
                            rand = random.randint(150,175)
                            if kazbal>=rand:
                                cursor.execute("UPDATE clandata SET balance=balance-? WHERE group_id=?", (rand, chid,))
                                conn.commit()
                            else:
                                if kazna>=2*rand:
                                    cursor.execute("UPDATE clandata SET balance=balance+? WHERE group_id=-1001395868701", (rand,))
                                    cursor.execute("UPDATE globaldata SET kazna=kazna-?", (2*rand,))
                                    conn.commit()
                                else:
                                    await message.answer('<i>К сожалению, у нас нет денег, чтобы выдать вознаграждение. Приходите позже или пожертвуйте деньги.\nПополнить баланс Игрового клуба можно, набрав сообщение <code>Пожертвовать [сумма]</code>. Пожертвовать деньги в казну можно через Банк</i>'.format(rand), parse_mode = 'html')
                                    return
                            await earn(message,rand)
                            await message.answer('<i><b>&#128176; Почти джекпот</b>\nВы выигрываете <b>${0}</b></i>'.format(rand), parse_mode = 'html')
                        elif value==22:
                            rand = random.randint(100,125)
                            if kazbal>=rand:
                                cursor.execute("UPDATE clandata SET balance=balance-? WHERE group_id=?", (rand,chid,))
                                conn.commit()
                            else:
                                if kazna>=2*rand:
                                    cursor.execute("UPDATE clandata SET balance=balance+? WHERE group_id=-1001395868701", (rand,))
                                    cursor.execute("UPDATE globaldata SET kazna=kazna-?", (2*rand,))
                                    conn.commit()
                                else:
                                    await message.answer('<i>К сожалению, у нас нет денег, чтобы выдать вознаграждение. Приходите позже или пожертвуйте деньги.\nПополнить баланс Игрового клуба можно, набрав сообщение <code>Пожертвовать [сумма]</code>. Пожертвовать деньги в казну можно через Банк</i>'.format(rand), parse_mode = 'html')
                                    return
                            await earn(message,rand)
                            await message.answer('<i><b>&#128176; Повезло!</b>\nВы выигрываете <b>${0}</b></i>'.format(rand), parse_mode = 'html')
                        elif value==1:
                            rand = random.randint(50,75)
                            if kazbal>=rand:
                                cursor.execute("UPDATE clandata SET balance=balance-? WHERE group_id=?", (rand,chid,))
                                conn.commit()
                            else:
                                if kazna>=2*rand:
                                    cursor.execute("UPDATE clandata SET balance=balance+? WHERE group_id=-1001395868701", (rand,))
                                    cursor.execute("UPDATE globaldata SET kazna=kazna-?", (2*rand,))
                                    conn.commit()
                                else:
                                    await message.answer('<i>К сожалению, у нас нет денег, чтобы выдать вознаграждение. Приходите позже или пожертвуйте деньги.\nПополнить баланс Игрового клуба можно, набрав сообщение <code>Пожертвовать [сумма]</code>. Пожертвовать деньги в казну можно через Банк</i>'.format(rand), parse_mode = 'html')
                                    return
                            await earn(message,rand)
                            await message.answer('<i><b>&#128077; Неплохо!</b>\nВы выигрываете <b>${0}</b></i>'.format(rand), parse_mode = 'html')
                    else:
                            await message.answer('<i>У вас недостаточно денег. Стоимость одной попытки: <b>$10</b></i>', parse_mode = 'html')
        except Exception as e:
            await message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    @bot.callback_query_handler()
    async def query_handler(call: types.CallbackQuery):
        await check(call.from_user.id, call.message.chat.id)
        a = call.from_user.id
        cursor.execute('SELECT prison FROM userdata WHERE user_id=?', (a,))
        prison = cursor.fetchone()[0]
        if prison>current_time():
            diff = prison-current_time()
            minutes = floor(diff/60)
            seconds = floor(diff%60)
            time = ''
            if minutes!=0:
                time+=' {0} минут'.format(minutes)
            if seconds!=0:
                time+=' {0} секунд'.format(seconds)
            await call.answer('❌ Вы были арестованы и теперь сидите в тюрьме. Вам осталось сидеть {0}'.format(time),show_alert = True)
            return
        if call.data.startswith('backup'):
            try:
                if call.from_user.id!=CREATOR:
                    await call.answer("❌ Эта команда доступна только создателю Живополиса :>", show_alert = True)
                    return
                markup = types.InlineKeyboardMarkup(row_width = 2)
                markup.add(types.InlineKeyboardButton(text = '💻 Код бота', callback_data='sendfile main.py'),
                           types.InlineKeyboardButton(text = '✏ Изменить код', callback_data='editfile_main.py'), 
                           types.InlineKeyboardButton(text = '🔧 Конфигурация', callback_data='sendfile config.py'),
                           types.InlineKeyboardButton(text = '✏ Изменить конфиг', callback_data='editfile_config.py'),
                          types.InlineKeyboardButton(text = '👤 База данных', callback_data='sendfile database.db'),
                          types.InlineKeyboardButton(text = '✏ Изменить БД', callback_data='editfile_database.db'),
                          types.InlineKeyboardButton(text = '♻ Перезагрузить бота', callback_data='restart_bot'),)
                await call.message.answer("<i>Вы можете сейчас получить или изменить нужный файл Живополиса. Но только если вы Микита Всемогущий</i>", parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('buy24_'):

        if call.data.startswith('buyclan_'):
            try:
                buyitem = call.data[8:]
                if not buyitem in clanitems:
                    return
                cost = clanitems[1][clanitems[0].index(buyitem)]
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance<cost:
                    await call.answer(text='❌ У вас недостаточно средств', show_alert = True)
                    return
                cursor.execute('UPDATE userdata SET balance=balance-? WHERE user_id=?', (cost, a,))
                conn.commit()
                cursor.execute('UPDATE userdata SET {0}={0}+1 WHERE user_id=?'.format(buyitem), (a,))
                conn.commit()
                cursor.execute('UPDATE clandata SET balance=balance+? WHERE group_id=?', (cost//2, chid,))
                conn.commit()
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                await call.answer(text='Покупка совершена успешно. Ваш баланс: ${0}. Баланс клана пополнен на ${1}'.format(balance, cost//2), show_alert = True)
            except Exception as e:
                await call.message.answer('<i><b>&#10060; Ошибка: </b>{0}</i>'.format(e), parse_mode = 'html');
        if call.data == 'drink_medicine':
            await cure(call.from_user.id, call.from_user.id, call.from_user.id)
        if call.data=='log_out':
            try:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='✅ Выйти из аккаунта', callback_data='log_out_confirm'))
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_action'))
                markup.add(types.InlineKeyboardButton(text='🔑 Установить ключ доступа', callback_data='set_user_key'))
                await call.message.answer('<i>Вы уверены, что хотите выйти из аккаунта? Вернуться назад вы сможете только если введёте ключ доступа (если у вас не установлен ключ доступа, вернуться назад в аккаунт не получится)</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('<i><b>&#10060; Ошибка: </b>{0}</i>'.format(e), parse_mode = 'html');
        if call.data=='delete_account':
            try:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='✅ Удалить аккаунт', callback_data='delete_account_confirm'))
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_action'))
                await call.message.answer('<i>Вы уверены, что хотите удалить свой аккаунт? Это действие невозможно будет отменить</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('<i><b>&#10060; Ошибка: </b>{0}</i>'.format(e), parse_mode = 'html');
        if call.data=='log_out_confirm':
            try:
                a = call.from_user.id
                if call.message.chat.type!='private':
                    await call.message.answer('<i>&#10060; Эта команда работает только в личных сообщениях с ботом</i>', parse_mode='html')
                    return
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                await main.send_message(fid, '<i><b><a href="tg://user?id={0}">{1}{2}</a></b> вышел(-а) из своего аккаунта\n#user_logout</i>'.format(a, rasa, nick), parse_mode='html')
                cursor.execute('SELECT id FROM userdata WHERE user_id = ?', (a,))
                ide = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET username="" WHERE user_id=?', (a,))
                conn.commit()
                cursor.execute('UPDATE userdata SET user_name="" WHERE user_id=?', (a,))
                conn.commit()
                cursor.execute('UPDATE userdata SET user_surname="" WHERE user_id=?', (a,))
                conn.commit()
                cursor.execute('UPDATE userdata SET user_id=0 WHERE id=?', (ide,))
                conn.commit()
                await call.message.answer('<i>&#9989; Вы были удалены из базы данных</i>', parse_mode = 'html');
            except Exception as e:
                await call.message.answer('<i><b>&#10060; Ошибка: </b>{0}</i>'.format(e), parse_mode = 'html');
        if call.data=='delete_account_confirm':
            try:
                a = call.from_user.id
                if call.message.chat.type!='private':
                    await call.message.answer('<i>&#10060; Эта команда работает только в личных сообщениях с ботом</i>', parse_mode='html')
                    return
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                await main.send_message(fid, '<i><b><a href="tg://user?id={0}">{1}{2}</a></b> удалил(-а) свой аккаунт\n#user_deauth</i>'.format(a, rasa, nick), parse_mode='html')
                cursor.execute('DELETE FROM userdata WHERE user_id=?', (a,))
                conn.commit()
                await call.message.answer('<i>&#9989; Ваш аккаунт был безвозвратно удалён из базы данных</i>', parse_mode = 'html');
            except Exception as e:
                await call.message.answer('<i><b>&#10060; Ошибка: </b>{0}</i>'.format(e), parse_mode = 'html');
        if call.data=='change_rasa':
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text='🐱 Кот', callback_data='cat'), 
                types.InlineKeyboardButton(text='🐶 Собака', callback_data='dog'),
                types.InlineKeyboardButton(text='🦝 Енот', callback_data='raccoon'),
                types.InlineKeyboardButton(text='🐸 Жаба', callback_data='frog'),
                types.InlineKeyboardButton(text='🦉 Сова', callback_data='owl'))
            await call.message.answer('<i>Выберите расу</i>', reply_markup = markup, parse_mode = 'html')
        if call.data == 'cat':
            await call.answer(text='Отличный выбор!')
            await setrasa(call.message, call.from_user, '&#128049', 0)
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'dog':
            await call.answer(text='Отличный выбор!')
            await setrasa(call.message, call.from_user, '&#128054', 1)
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'raccoon':
            await call.answer(text='Отличный выбор!')
            await setrasa(call.message, call.from_user, '&#129437', 2)
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'frog':
            await call.answer(text='Отличный выбор!')
            await setrasa(call.message, call.from_user, '&#128056;', 3)
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'owl':
            await call.answer(text='Отличный выбор!')
            await setrasa(call.message, call.from_user, '&#129417;', 4)
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'set_user_profile':
            try:
                markup = types.InlineKeyboardMarkup()
                a = call.from_user.id
                markup.add(types.InlineKeyboardButton(text='👤 Изменить ник', callback_data='set_user_nick'))
                markup.add(types.InlineKeyboardButton(text='📃 Изменить описание', callback_data='set_user_bio'))
                markup.add(types.InlineKeyboardButton(text='🤡 Изменить расу', callback_data='change_rasa'))
                markup.add(types.InlineKeyboardButton(text='🖼 Изменить фото профиля', callback_data='set_user_photo'))
                await call.message.answer('<i><b>Настройки</b>\nИзменить ник: <code>/nick [ник]</code>\nИзменить описание профиля: <code>/bio [описание]</code>\nВыбрать расу: <code>Раса</code></i>', parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'user_settings':
            try:
                markup = types.InlineKeyboardMarkup()
                a = call.from_user.id
                cursor.execute('SELECT ready FROM userdata WHERE user_id=?', (a,))
                ready = cursor.fetchone()[0]
                markup.add(types.InlineKeyboardButton(text='⚔ Боевая готовность: {0}'.format('Готов' if ready==1 else 'Не готов'), callback_data='set_user_mode'))
                markup.add(types.InlineKeyboardButton(text='🤡 Настройки профиля', callback_data='set_user_profile'))
                markup.add(types.InlineKeyboardButton(text='🔐 Конфиденциальность', callback_data='set_user_privacy'))
                await call.message.answer('<i><b>Настройки</b></i>', parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'set_user_privacy':
            try:
                markup = types.InlineKeyboardMarkup()
                a = call.from_user.id
                cursor.execute('SELECT type FROM userdata WHERE user_id=?', (a,))
                ready = cursor.fetchone()[0]
                markup.add(types.InlineKeyboardButton(text='🔐 Тип профиля: {0}'.format('Открытый' if ready=='public' else 'Закрытый'), callback_data='set_user_type'))
                markup.add(types.InlineKeyboardButton(text='🔑 Ключ доступа', callback_data='set_user_key'))
                markup.add(types.InlineKeyboardButton(text='🔙 Выйти из аккаунта', callback_data='log_out'))
                markup.add(types.InlineKeyboardButton(text='🗑 Удалить аккаунт', callback_data='delete_account'))
                await call.message.answer('<i><b>Настройки конфиденциальности</b></i>', parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('buy_medicine_'):
            amr = int(call.data[13:])
            await buy(call, user=call.from_user, item='medicine', cost=500, amount=amr)
        if call.data.startswith('trolleybus_'):
            try:
                if not isinterval('trolleybus'):
                    await call.answer('Посадка ещё не началась. Троллейбус приедет через {0}'.format(remaining('trolleybus')), show_alert = True)
                    return
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                chid = call.message.chat.id
                dest = call.data[11:]
                ind = CITY.index(station)
                if dest=='forward':
                    nextstation = CITY[ind+1]
                else:
                    nextstation = CITY[ind-1]
                await main.delete_message(call.message.chat.id, call.message.message_id)
                await main.send_photo(chid, 'https://telegra.ph/file/411dad335dac249f8b1aa.jpg', caption='<i>Следующая остановка: <b>{0}</b>. Осторожно, двери закрываются!</i>'.format(nextstation), parse_mode='html')
                await asyncio.sleep(random.randint(lessbus, morebus))
                cursor.execute('UPDATE userdata SET place=? WHERE user_id=?', (nextstation,a,))
                conn.commit()
                await buscall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'market_mask':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                place = cursor.fetchone()[0]
                if place!='Рынок':
                    return
                markup = types.InlineKeyboardMarkup(row_width = 3)
                itemlist = []
                cursor.execute('SELECT coef FROM globaldata')
                coef = cursor.fetchone()[0]
                for inst in ITEMS[1]:
                    ind = ITEMS[1].index(inst)
                    if itemdata(a, inst)!='emptyslot' and ITEMS[4][ind] == 'mask' and ITEMS[3][ind] > 0:
                        cost = int(ITEMS[3][ind]/coef)
                        itemlist.append(types.InlineKeyboardButton(text='{0} - ${1}'.format(ITEMS[0][ind], cost), callback_data='sellitem_{0}'.format(inst)))
                if itemlist==[]:
                    desc = '❌ У вас нет масок для продажи'
                else:
                    markup.add(*itemlist)
                    desc = '<b>🏣 Центральный рынок</b> - место, в котором можно продать купленные товары. Дешевле, чем в магазине, но удобно\n\n❗ Здесь вы <b>продаёте</b> товары государству, а не покупаете. Деньги вы получаете автоматически, ваш товар никому не достаётся'
                markup.add(types.InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))
                await call.message.answer('<i>{0}</i>'.format(desc), reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')

        if call.data == 'darkweb':
            try:
                a = call.from_user.id
                cursor.execute('SELECT key FROM userdata WHERE user_id = ?', (a,))
                key = cursor.fetchone()[0]
                if key == 0:
                    await call.message.answer('<i>&#10060; У вас нет этого предмета</i>', reply_markup = markup, parse_mode = 'html')
                    return
                await achieve(call.from_user.id, call.message.chat.id, 'black')
                markup = types.InlineKeyboardMarkup()
                markup.add(buybutton('msk'))
                markup.add(buybutton('pistol'))
                markup.add(buybutton('bron'))
                markup.add(buybutton('bomb'))
                markup.add(buybutton('workers'))
                markup.add(buybutton('truck'))
                markup.add(buybutton('poison'))
                await main.send_message(call.from_user.id, '<i>&#128272; Что хотите прикупить?</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'shop_24':
            markup = types.InlineKeyboardMarkup()
            markup.add(buybutton('bread', 'limited'))
            markup.add(buybutton('pelmeni', 'limited'))
            markup.add(buybutton('soup', 'limited'))
            markup.add(buybutton('meat', 'limited'))
            markup.add(buybutton('meatcake', 'limited'))
            markup.add(buybutton('tea', 'limited'))
            await call.message.answer('<i>Что хотите купить?</i>', reply_markup = markup, parse_mode = 'html')
        if call.data == 'farm':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Роща':
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='🐄 Подоить корову', callback_data='milk_cow'))
                await call.message.answer('<i>&#127806; Добро пожаловать на ферму! Здесь можно подоить корову и просто подышать свежим воздухом!</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'milk_cow':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Роща':
                    return
                cursor.execute('SELECT cow FROM userdata WHERE user_id=?', (a,))
                cow = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                if cow<1:
                    markup.add(types.InlineKeyboardButton(text='🌾 Вернуться на ферму', callback_data='farm'))
                    await call.message.answer('<i>&#128004; К сожалению, у вас нет коров :(</i>', reply_markup = markup, parse_mode = 'html')
                    return
                else:
                    markup.add(types.InlineKeyboardButton(text='🥛 Доить', callback_data='milk_cow_confirm'))
                    await call.message.answer('<i>&#128004; У вас <b>{0}</b> коров. При дойке у вас заберётся одна корова, а взамен вы получите стакан молока</i>'.format(cow), reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'milk_cow_confirm':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Роща':
                    return
                cursor.execute('SELECT cow FROM userdata WHERE user_id=?', (a,))
                cow = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                if cow<1:
                    markup.add(types.InlineKeyboardButton(text='🌾 Вернуться на ферму', callback_data='farm'))
                    await call.message.answer('<i>&#128004; К сожалению, у вас нет коров :(</i>', reply_markup = markup, parse_mode = 'html')
                    return
                else:
                    await call.message.answer('<i>&#128004; Дойка продлится около 10 секунд</i>', parse_mode = 'html')
                    await asyncio.sleep(10)
                    cursor.execute('UPDATE userdata SET cow=cow-1 WHERE user_id=?', (a,))
                    cursor.execute('UPDATE userdata SET milk=milk+1 WHERE user_id=?', (a,))
                    conn.commit()
                    await call.message.answer('<i>&#128004; Дойка прошла успешно</i>', parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'gps':
            try:
                a = call.from_user.id
                cursor.execute('SELECT phone FROM userdata WHERE user_id=?', (a,))
                phone = cursor.fetchone()[0]
                if phone<1:
                    await call.answer('Чтобы пользоваться GPS, вам нужен телефон. Его можно купить в магазине на ул. Генерала Шелби и одноимённой станции метро', show_alert = True)
                    return
                categorylist = []
                markup = types.InlineKeyboardMarkup()
                for category in locations[3]:
                    if not category in categorylist:
                        categorylist.append(category)
                        count = 0
                        for location in locations[0]:
                            if locations[3][locations[0].index(location)] == category:
                                count+=1
                        markup.add(types.InlineKeyboardButton(text='{0} ({1})'.format(category, count), callback_data='gpsloc_{0}'.format(category)))
                markup.add(types.InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))
                await call.message.answer('<i>Выберите категорию</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('gpsloc_'):
            try:
                a = call.from_user.id
                cursor.execute('SELECT phone FROM userdata WHERE user_id=?', (a,))
                phone = cursor.fetchone()[0]
                if phone<1:
                    await call.answer('Чтобы пользоваться GPS, вам нужен телефон. Его можно купить в магазине на ул. Генерала Шелби и одноимённой станции метро', show_alert = True)
                    return
                category = call.data.replace('gpsloc_', '')
                ls = []
                for location in locations[0]:
                    if locations[3][locations[0].index(location)] == category:
                        ls.append(types.InlineKeyboardButton(text=location, callback_data='location_{0}'.format(location)))
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(*ls)
                markup.add(types.InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))
                await call.message.answer('<i>Выберите локацию</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('location_'):
            try:
                a = call.from_user.id
                cursor.execute('SELECT phone FROM userdata WHERE user_id=?', (a,))
                phone = cursor.fetchone()[0]
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                place = cursor.fetchone()[0]
                if phone<1:
                    await call.answer('Чтобы пользоваться GPS, вам нужен телефон. Его можно купить в магазине на ул. Генерала Шелби и одноимённой станции метро', show_alert = True)
                    return
                location = call.data.replace('location_', '')
                if not location in locations[0]:
                    return
                ind = locations[0].index(location)
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))
                await call.message.answer('<i><b>{0}</b>\n\n{1}\n🏛 Местность: <b>{2}</b>\n\nТранспорт рядом:\n{3}</i>'.format(locations[0][ind], locations[1][ind], locations[2][ind], access(locations[2][ind], place)), reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'mask_clothes':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='ТЦ МиГ':
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(buybutton('clown'))
                markup.add(buybutton('ghost'))
                markup.add(buybutton('alien'))
                markup.add(buybutton('robot'))
                markup.add(buybutton('shit'))
                markup.add(buybutton('moyai'))
                await call.message.answer('<i>Что хотите купить?</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'enot_kebab':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if not station in villages and not station in trains[0]:
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(buybutton('burger'))
                markup.add(buybutton('shaurma'))
                markup.add(buybutton('fries'))
                markup.add(buybutton('cheburek'))
                markup.add(buybutton('beer'))
                await call.message.answer('<i>Что хотите купить?</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'car_park':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Автопарк им. Кота':
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(buybutton('car'))
                markup.add(buybutton('bluecar'))
                await call.message.answer('<i>Какую машину хотите купить?</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'hospital':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Райбольница' and station!='Старокотайский ФАП':
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='💊 Таблетка Котробене - $500', callback_data='buy_medicine_1'))
                markup.add(types.InlineKeyboardButton(text='💊 Маленькая пачка (5 шт.) - $2500', callback_data='buy_medicine_5'))
                markup.add(types.InlineKeyboardButton(text='💊 Баночка (10 шт.) - $5000', callback_data='buy_medicine_10'))
                await call.message.answer('<i>Что хотите приобрести?</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'zoo':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Зоопарк':
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(buybutton('morj'))
                markup.add(buybutton('cow'))
                markup.add(buybutton('yozh'))
                markup.add(buybutton('wolf'))
                markup.add(buybutton('fox'))
                markup.add(buybutton('hamster'))
                await call.message.answer('<i>Что хотите купить?</i>', reply_markup=markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'botan_garden':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Ботаническая':
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(buybutton('clover'))
                markup.add(buybutton('palm'))
                markup.add(buybutton('rose'))
                markup.add(buybutton('tulip'))
                markup.add(buybutton('houseplant'))
                markup.add(buybutton('cactus'))
                await call.message.answer('<i>Что хотите купить?</i>', reply_markup=markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'rob_bank_confirm':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                cursor.execute('SELECT balance from userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if station!='Живбанк':
                    return
                rand = random.randint(1,5)
                if rand<5:
                    if balance>=150:
                        cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance-150, a,))
                        cursor.execute('UPDATE globaldata SET kazna=kazna+75')
                        conn.commit()
                        await call.message.answer('<i>У вас не получилось ограбить банк. За это мы сняли у вас с баланса <b>$150</b></i>', parse_mode='html')
                    else:
                        cursor.execute('UPDATE userdata SET prison=? WHERE user_id=?', (current_time()+900, a,))
                        conn.commit()
                        cursor.execute('SELECT rasa from userdata WHERE user_id=?', (a,))
                        rasa = cursor.fetchone()[0]
                        cursor.execute('SELECT nick from userdata WHERE user_id=?', (a,))
                        nick = cursor.fetchone()[0]
                        await call.message.answer('<i>&#128110; Господин <b><a href="tg://user?id={0}">{1}{2}</a></b>, вы задержаны за попытку ограбления банка. Пройдёмте в отделение.\n\nВы были арестованы на <b>15 минут</b></i>'.format(a, rasa, nick), parse_mode='html')
                if rand>=5:
                    rando = random.randint(150, 550)
                    cursor.execute("SELECT kazna FROM globaldata")
                    kazna = cursor.fetchone()[0]
                    if kazna>=rando:
                        await call.message.answer('<i>&#127942; У вас получилось ограбить банк! Вы унесли с собой <b>${0}</b></i>'.format(rando), parse_mode='html')
                        cursor.execute('UPDATE globaldata SET kazna=kazna-?', (rando,))
                        cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance+rando, a,))
                        conn.commit()
                    else:
                        await call.message.answer('&#10060; <i>А что вы грабить собрались? Казна пуста</i>', parse_mode='html')
                await main.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'rob_bank':
            try:
                a = call.from_user.id
                items = 0
                cursor.execute('SELECT msk from userdata WHERE user_id=?', (a,))
                items += 1 if cursor.fetchone()[0]>=1 else 0
                cursor.execute('SELECT pistol from userdata WHERE user_id=?', (a,))
                items += 1 if cursor.fetchone()[0]>=1 else 0
                cursor.execute('SELECT bomb from userdata WHERE user_id=?', (a,))
                items += 1 if cursor.fetchone()[0]>=1 else 0
                cursor.execute('SELECT truck from userdata WHERE user_id=?', (a,))
                items += 1 if cursor.fetchone()[0]>=1 else 0
                cursor.execute('SELECT workers from userdata WHERE user_id=?', (a,))
                items += 1 if cursor.fetchone()[0]>=1 else 0
                cursor.execute('SELECT bron from userdata WHERE user_id=?', (a,))
                items += 1 if cursor.fetchone()[0]>=1 else 0
                if items<6:
                    await call.message.answer('<i>&#10060; У вас недостаточно предметов для кражи. Вам нужны:\n<b>&#128666; Грузовик\n&#128299; Пистолет\n&#128163; Бомба\n&#129466; Бронежилет\n&#128122; Маска\n&#128104; Наёмники\n</b>Всё это можно приобрести в <b>[данные засекречены]</b></i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Живбанк':
                    return
                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton(text='🤏', callback_data='rob_bank_confirm'), types.InlineKeyboardButton(text='🤏', callback_data='rob_bank_confirm'), types.InlineKeyboardButton(text='🤏', callback_data='rob_bank_confirm'))
                markup.row(types.InlineKeyboardButton(text='🤏', callback_data='rob_bank_confirm'), types.InlineKeyboardButton(text='🤏', callback_data='rob_bank_confirm'))
                await call.message.answer('<i>🤏 Нажмите на кнопочку. Если повезёт, банк ограбится!</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data=='go_out':
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'university':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Университет':
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='➕ Математика', callback_data='play_math'))
                markup.add(types.InlineKeyboardButton(text='🌍 География', callback_data='play_geo'))
                await call.message.answer('<i>🏫 <b>Добро пожаловать в Живополисский университет</b>\nЗдесь коты, собаки, еноты, совы и жабы (шучу, жаб там нет :) получают новые знания и опыт с помощью мини-игр.\n\nВыберите мини-игру. Учтите, что у вас должно быть не менее $10 на балансе, чтобы играть</i>', reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'factory':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                cursor.execute('SELECT electimes from userdata WHERE user_id=?', (a,))
                times = cursor.fetchone()[0]
                if station!='Котайский электрозавод':
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='⚙ Шестерёнки', callback_data='play_plant'))
                await call.message.answer('<i>🏭 <b>Добро пожаловать на Завод</b>\nЗдесь вы можете заработать немного денег, если зарплаты офисного работника не хватает.\n\nВыберите мини-игру. Учтите, что у вас должно быть не менее $10 на балансе, чтобы играть.\n\nИграть можно не более 10 раз в день. Сегодня вы уже играли <b>{0}</b> раз</i>'.format(times), reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'play_math':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Университет':
                    return
                cursor.execute('SELECT balance from userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT lastplay from userdata WHERE user_id=?', (a,))
                lastplay = cursor.fetchone()[0]
                diff = int(current_time()-lastplay)
                if diff<45*60:
                    await call.answer('❌ Вы были наказаны за неверный ответ. До снятия наказания осталось {0} минут {1} секунд'.format(45-ceil(diff/60), 60-ceil(diff%60)), show_alert = True)
                    return
                if balance<10:
                    await call.answer('❌ Вы не можете играть в эту мини-игру, т.к. у вас меньше $10 на балансе', show_alert = True)
                    return
                operation = random.choice(['+', '-'])
                op1 = random.randint(50, 150)
                op2 = random.randint(50, 150)
                min = random.choice([0, 0, 0, 0, 0, 0, 0, 10, 20, -10, 5, -5, 10, -10, 2, -2])
                if operation == '+':
                    sum = op1+op2+min
                    real=op1+op2
                else:
                    sum = op1-op2+min
                    real=op1-op2
                cr = []
                markup = types.InlineKeyboardMarkup(row_width=2)
                cr.append(types.InlineKeyboardButton(text='Да', callback_data='mathres correct {0} {1} {2} {3} 1'.format(op1, operation, op2, sum)))
                cr.append(types.InlineKeyboardButton(text='Нет', callback_data='mathres wrong {0} {1} {2} {3} 1'.format(op1, operation, op2, sum)))
                markup.add(*cr)
                cr = []
                marc = types.InlineKeyboardMarkup(row_width=2)
                cr.append(types.InlineKeyboardButton(text='Да', callback_data='mathres correct {0} {1} {2} {3} 2'.format(op1, operation, op2, sum)))
                cr.append(types.InlineKeyboardButton(text='Нет', callback_data='mathres wrong {0} {1} {2} {3} 2'.format(op1, operation, op2, sum)))
                marc.add(*cr)
                seconds = 0
                msg = await call.message.answer('<i><b>Верно ли утверждение?</b>\n{0} {1} {2} = {3}</i>'.format(op1, operation, op2, sum), reply_markup = markup, parse_mode = 'html')
                beginning = current_time()
                for seconds in range(1,11):
                    cursor.execute('SELECT lastmath from userdata WHERE user_id=?', (a,))
                    lastmath = cursor.fetchone()[0]
                    if lastmath!=msg['message_id']:
                        if seconds<=4:
                            current_mc = marc
                            nagrada = 'Верно ответьте на вопрос в течение первых 4 секунд, чтобы получить награду 💡 <b>8 очков</b>'
                        else:
                            current_mc = markup
                            nagrada = 'Награда за верный ответ: 💡 <b>4 очка</b>'
                        await main.edit_message_text(chat_id = call.message.chat.id, message_id = msg['message_id'], text = '<i><b>Верно ли утверждение?</b>\n{0} {1} {2} = {3}\n\nОтветьте на вопрос, пока все квадратики не заполнятся:\n{4}{5}\n\n{6}</i>'.format(op1, operation, op2, sum, '🔳'*seconds, '◻'*(10-seconds), nagrada), reply_markup = current_mc, parse_mode = 'html')
                        await asyncio.sleep(1)
                    else:
                        break
                cursor.execute('SELECT lastmath from userdata WHERE user_id=?', (a,))
                lastmath = cursor.fetchone()[0]
                if msg['message_id']!=lastmath:
                    await asyncio.sleep(1)
                    mark = types.InlineKeyboardMarkup(row_width = 2)
                    cr = []
                    if sum==real:
                        cr.append(types.InlineKeyboardButton(text='Да✅', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет❌', callback_data='alreadyno'))
                        ans = '<b>✅ Да</b>\n{0} {1} {2} = <b>{3}</b>'.format(op1, operation, op2, real)
                    else:
                        cr.append(types.InlineKeyboardButton(text='Да❌', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет✅', callback_data='alreadyno'))
                        ans = '<b>❌ Нет</b>\n{0} {1} {2} = <del>{3}</del> <b>{4}</b>'.format(op1, operation, op2, sum, real)
                    mark.add(*cr)
                    your = '<code>Вы не дали ответа.\n💲 Штраф за отсутствие ответа: $5</code>'
                    cursor.execute('UPDATE userdata SET balance=balance-5 WHERE user_id=?', (a,))
                    conn.commit()
                    mark.add(types.InlineKeyboardButton(text='🔄 Заново', callback_data='play_math'))
                    await call.answer('Раунд закончен')
                    cursor.execute("UPDATE userdata SET lastplay = ? WHERE user_id = ?", (current_time(),a,))
                    conn.commit()
                    await main.edit_message_text(chat_id = call.message.chat.id, message_id = msg['message_id'], text = '<i><b>Верно ли утверждение?</b>\n\nВерный ответ: {0}\n\n{1}</i>'.format(ans, your), reply_markup = mark, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'alreadyno':
            await call.answer('А уже нельзя :)')
        if call.data.startswith('mathres '):
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Университет':
                    return
                cursor.execute('SELECT balance from userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance<10:
                    await call.answer('❌ Вы не можете играть в эту мини-игру, т.к. у вас меньше $10 на балансе', show_alert = True)
                    return
                cursor.execute('UPDATE userdata SET lastmath=? WHERE user_id=?', (call.message.message_id, a,))
                conn.commit()
                res = call.data.split(' ')
                iscorrect = True if res[1]=='correct' else False
                op1 = int(res[2])
                operation = res[3]
                op2 = int(res[4])
                sum = int(res[5])
                bonus = int(res[6])
                if operation == '+':
                    real = op1+op2
                else:
                    real = op1-op2
                cr = []
                points = 4*bonus
                markup = types.InlineKeyboardMarkup(row_width=2)
                if iscorrect:
                    if sum==real:
                        cr.append(types.InlineKeyboardButton(text='Да✅', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет', callback_data='alreadyno'))
                        await call.answer('Правильно!')
                    else:
                        cr.append(types.InlineKeyboardButton(text='Да❌', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет', callback_data='alreadyno'))
                        await call.answer('Неправильно!')
                else:
                    if sum!=real:
                        cr.append(types.InlineKeyboardButton(text='Да', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет✅', callback_data='alreadyno'))
                        await call.answer('Правильно!')
                    else:
                        cr.append(types.InlineKeyboardButton(text='Да', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет❌', callback_data='alreadyno'))
                        await call.answer('Неправильно!')
                markup.add(*cr)
                markup.add(types.InlineKeyboardButton(text='🔄 Заново', callback_data='play_math'))
                if sum == real:
                    ans = '<b>✅ Да</b>\n{0} {1} {2} = <b>{3}</b>'.format(op1, operation, op2, real)
                else:
                    ans = '<b>❌ Нет</b>\n{0} {1} {2} = <del>{3}</del> <b>{4}</b>'.format(op1, operation, op2, sum, real)
                if (sum == real and iscorrect) or (sum != real and not iscorrect):
                    nagrada = ''
                    if bonus==2:
                        nagrada='\nБонус за быстрый ответ: 4 очка'
                    your = '<code>Ваш ответ верен.\n💡 Награда за верный ответ: 4 очка{0}\n\nИтого: {1} очков</code>'.format(nagrada, points)
                    cursor.execute('UPDATE userdata SET points=points+? WHERE user_id=?', (points, a,))
                    conn.commit()
                else:
                    your = '<code>Ваш ответ неверен.\n💲 Штраф за неверный ответ: $10</code>'
                    cursor.execute('UPDATE userdata SET balance=balance-10 WHERE user_id=?', (a,))
                    conn.commit()
                    cursor.execute("UPDATE userdata SET lastplay = ? WHERE user_id = ?", (current_time(),a,))
                    conn.commit()
                msg = await main.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '<i><b>Верно ли утверждение?</b>\n\nВерный ответ: {0}\n\n{1}</i>'.format(ans, your), reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'play_geo':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Университет':
                    return
                cursor.execute('SELECT balance from userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance<10:
                    await call.answer('❌ Вы не можете играть в эту мини-игру, т.к. у вас меньше $10 на балансе', show_alert = True)
                    return
                cursor.execute('SELECT lastplay from userdata WHERE user_id=?', (a,))
                lastplay = cursor.fetchone()[0]
                diff = int(current_time()-lastplay)
                if diff<45*60:
                    await call.answer('❌ Вы были наказаны за неверный ответ. До снятия наказания осталось {0} минут {1} секунд'.format(45-ceil(diff/60), 60-diff%60), show_alert = True)
                    return
                country = countries.index(random.choice(countries))
                situation = random.choice([0, 1])
                if situation == 0:
                    capital = country
                else:
                    capital = capitals.index(random.choice(capitals))
                cr = []
                markup = types.InlineKeyboardMarkup(row_width=2)
                cr.append(types.InlineKeyboardButton(text='Да', callback_data='geores correct {0} {1}'.format(country, capital)))
                cr.append(types.InlineKeyboardButton(text='Нет', callback_data='geores wrong {0} {1}'.format(country, capital)))
                markup.add(*cr)
                seconds = 0
                msg = await call.message.answer('<i><b>Верно ли утверждение?</b>\nСтолицей государства <b>{0}</b> является <b>{1}</b></i>'.format(countries[country], capitals[capital]), reply_markup = markup, parse_mode = 'html')
                beginning = current_time()
                for seconds in range(1,11):
                    cursor.execute('SELECT lastmath from userdata WHERE user_id=?', (a,))
                    lastmath = cursor.fetchone()[0]
                    if lastmath!=msg['message_id']:
                        current_mc = markup
                        nagrada = 'Награда за верный ответ: 💡 <b>4 очка</b>'
                        await main.edit_message_text(chat_id = call.message.chat.id, message_id = msg['message_id'], text = '<i><b>Верно ли утверждение?</b>\nСтолицей государства <b>{0}</b> является <b>{1}</b>\n\nОтветьте на вопрос, пока все квадратики не заполнятся:\n{2}{3}\n\n{4}</i>'.format(countries[country], capitals[capital], '🔳'*seconds, '◻'*(10-seconds), nagrada), reply_markup = current_mc, parse_mode = 'html')
                        await asyncio.sleep(1)
                    else:
                        break
                cursor.execute('SELECT lastmath from userdata WHERE user_id=?', (a,))
                lastmath = cursor.fetchone()[0]
                if msg['message_id']!=lastmath:
                    await asyncio.sleep(1)
                    mark = types.InlineKeyboardMarkup(row_width = 2)
                    cr = []
                    if country==capital:
                        cr.append(types.InlineKeyboardButton(text='Да✅', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет❌', callback_data='alreadyno'))
                        ans = '<b>✅ Да</b>\nСтолицей государства <b>{0}</b> является <b>{1}</b>'.format(countries[country], capitals[capital])
                    else:
                        cr.append(types.InlineKeyboardButton(text='Да❌', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет✅', callback_data='alreadyno'))
                        ans = '<b>❌ Нет</b>\nСтолицей государства <b>{0}</b> являетя <del>{1}</del> <b>{2}</b>.\n<b>{1}</b> является столицей государства <b>{3}</b>'.format(countries[country], capitals[capital], capitals[country], countries[capital])
                    mark.add(*cr)
                    your = '<code>Вы не дали ответа.\n💲 Штраф за отсутствие ответа: $5</code>'
                    cursor.execute('UPDATE userdata SET balance=balance-5 WHERE user_id=?', (a,))
                    conn.commit()
                    mark.add(types.InlineKeyboardButton(text='🔄 Заново', callback_data='play_geo'))
                    await call.answer('Раунд закончен')
                    await main.edit_message_text(chat_id = call.message.chat.id, message_id = msg['message_id'], text = '<i><b>Верно ли утверждение?</b>\n\nВерный ответ: {0}\n\n{1}</i>'.format(ans, your), reply_markup = mark, parse_mode = 'html')
                    cursor.execute("UPDATE userdata SET lastplay = ? WHERE user_id = ?", (current_time(),a,))
                    conn.commit()
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('geores '):
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Университет':
                    return
                cursor.execute('SELECT balance from userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance<10:
                    await call.answer('❌ Вы не можете играть в эту мини-игру, т.к. у вас меньше $10 на балансе', show_alert = True)
                    return
                cursor.execute('UPDATE userdata SET lastmath=? WHERE user_id=?', (call.message.message_id, a,))
                conn.commit()
                res = call.data.split(' ')
                iscorrect = True if res[1]=='correct' else False
                country = int(res[2])
                capital = int(res[3])
                cr = []
                points = 4
                markup = types.InlineKeyboardMarkup(row_width=2)
                if iscorrect:
                    if capital==country:
                        cr.append(types.InlineKeyboardButton(text='Да✅', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет', callback_data='alreadyno'))
                        await call.answer('Правильно!')
                    else:
                        cr.append(types.InlineKeyboardButton(text='Да❌', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет', callback_data='alreadyno'))
                        await call.answer('Неправильно!')
                else:
                    if capital!=country:
                        cr.append(types.InlineKeyboardButton(text='Да', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет✅', callback_data='alreadyno'))
                        await call.answer('Правильно!')
                    else:
                        cr.append(types.InlineKeyboardButton(text='Да', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='Нет❌', callback_data='alreadyno'))
                        await call.answer('Неправильно!')
                markup.add(*cr)
                markup.add(types.InlineKeyboardButton(text='🔄 Заново', callback_data='play_geo'))
                if capital == country:
                    ans = '<b>✅ Да</b>\nСтолицей государства <b>{0}</b> является <b>{1}</b>'.format(countries[country], capitals[capital])
                else:
                    ans = '<b>❌ Нет</b>\nСтолицей государства <b>{0}</b> является <del>{1}</del> <b>{2}</b>.\n<b>{1}</b> является столицей государства <b>{3}</b>'.format(countries[country], capitals[capital], capitals[country], countries[capital])
                if (country == capital and iscorrect) or (country != capital and not iscorrect):
                    your = '<code>Ваш ответ верен.\n💡 Награда за верный ответ: 4 очка</code>'
                    cursor.execute('UPDATE userdata SET points=points+? WHERE user_id=?', (points, a,))
                    conn.commit()
                else:
                    your = '<code>Ваш ответ неверен.\n💲 Штраф за неверный ответ: $10</code>'
                    cursor.execute('UPDATE userdata SET balance=balance-10 WHERE user_id=?', (a,))
                    conn.commit()
                    cursor.execute("UPDATE userdata SET lastplay = ? WHERE user_id = ?", (current_time(),a,))
                    conn.commit()
                msg = await main.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '<i><b>Верно ли утверждение?</b>\n\nВерный ответ: {0}\n\n{1}</i>'.format(ans, your), reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'play_plant':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Котайский электрозавод':
                    return
                cursor.execute('SELECT balance from userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance<10:
                    await call.answer('❌ Вы не можете играть в эту мини-игру, т.к. у вас меньше $10 на балансе', show_alert = True)
                    return
                cursor.execute('SELECT lastelec from userdata WHERE user_id=?', (a,))
                lastplay = cursor.fetchone()[0]
                cursor.execute('SELECT electimes from userdata WHERE user_id=?', (a,))
                electimes = cursor.fetchone()[0]
                diff = int(current_time()-lastplay)
                if diff<3600*24 and electimes>=10:
                    await call.answer('❌ На Заводе можно работать не более 10 раз в сутки. До следующей возможности работать осталось {0} часов {1} минут {2} секунд'.format(24-ceil(diff/3600), 60-ceil(diff%3600/60), 60-ceil(diff%3600%60)), show_alert = True)
                    return
                dir = random.choice(['left', 'right'])
                dirn = '↩' if dir=='left' else '↪'
                amount = random.randint(2, 7)
                cr = []
                markup = types.InlineKeyboardMarkup(row_width=2)
                cr.append(types.InlineKeyboardButton(text='↩', callback_data='plantres left {0} {1}'.format(dir, amount)))
                cr.append(types.InlineKeyboardButton(text='↪', callback_data='plantres right {0} {1}'.format(dir, amount)))
                markup.add(*cr)
                seconds = 0
                msg = await call.message.answer('<i><b>В какую сторону будет вращаться белый круг?</b>\n{0}{1}⚪</i>'.format(dirn, '⚙'*amount), reply_markup = markup, parse_mode = 'html')
                beginning = current_time()
                for seconds in range(1,8):
                    cursor.execute('SELECT lastmath from userdata WHERE user_id=?', (a,))
                    lastmath = cursor.fetchone()[0]
                    if lastmath!=msg['message_id']:
                        current_mc = markup
                        nagrada = '💲 Награда за верный ответ: <b>$15</b>'
                        await main.edit_message_text(chat_id = call.message.chat.id, message_id = msg['message_id'], text = '<i><b>В какую сторону будет вращаться белый круг?</b>\n{0}{1}⚪\n\nОтветьте на вопрос, пока все квадратики не заполнятся:\n{2}{3}\n\n{4}</i>'.format(dirn, '⚙'*amount, '🔳'*seconds, '◻'*(7-seconds), nagrada), reply_markup = current_mc, parse_mode = 'html')
                        await asyncio.sleep(1)
                    else:
                        break
                cursor.execute('SELECT lastmath from userdata WHERE user_id=?', (a,))
                lastmath = cursor.fetchone()[0]
                if msg['message_id']!=lastmath:
                    await asyncio.sleep(1)
                    mark = types.InlineKeyboardMarkup(row_width = 2)
                    cr = []
                    if (amount%2==1 and dir=='left') or (amount%2==0 and dir=='right'):
                        cr.append(types.InlineKeyboardButton(text='↩✅', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='↪❌', callback_data='alreadyno'))
                        ans = '<b>↩</b>\n{0}{1}↩'.format(dirn, '⚙'*amount)
                    else:
                        cr.append(types.InlineKeyboardButton(text='↩❌', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='↪✅', callback_data='alreadyno'))
                        ans = '<b>↪</b>\n{0}{1}↪'.format(dirn, '⚙'*amount)
                    mark.add(*cr)
                    your = '<code>Вы не дали ответа.\n💲 Штраф за отсутствие ответа: $5</code>'
                    cursor.execute('UPDATE userdata SET balance=balance-5 WHERE user_id=?', (a,))
                    conn.commit()
                    mark.add(types.InlineKeyboardButton(text='🔄 Заново', callback_data='play_plant'))
                    await call.answer('Раунд закончен')
                    await main.edit_message_text(chat_id = call.message.chat.id, message_id = msg['message_id'], text = '<i><b>В какую сторону будет вращаться белый круг?</b>\n\nВерный ответ: {0}\n\n{1}</i>'.format(ans, your), reply_markup = mark, parse_mode = 'html')
                    cursor.execute("UPDATE userdata SET electimes=electimes+1 WHERE user_id = ?", (a,))
                    conn.commit()
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('plantres '):
            try:
                a = call.from_user.id
                cursor.execute('SELECT place from userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                if station!='Котайский электрозавод':
                    return
                cursor.execute('SELECT balance from userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance<10:
                    await call.answer('❌ Вы не можете играть в эту мини-игру, т.к. у вас меньше $10 на балансе', show_alert = True)
                    return
                cursor.execute('UPDATE userdata SET lastmath=? WHERE user_id=?', (call.message.message_id, a,))
                conn.commit()
                res = call.data.split(' ')
                ansr = res[1]
                dir = res[2]
                amount = int(res[3])
                dirn = '↩' if dir=='left' else '↪'
                cr = []
                earning = 15
                markup = types.InlineKeyboardMarkup(row_width=2)
                if (amount%2==1 and dir=='left') or (amount%2==0 and dir=='right'):
                    correct_answer='left'
                else:
                    correct_answer='right'
                if ansr=='left':
                    if correct_answer=='left':
                        cr.append(types.InlineKeyboardButton(text='↩✅', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='↪', callback_data='alreadyno'))
                        await call.answer('Правильно!')
                    else:
                        cr.append(types.InlineKeyboardButton(text='↩❌', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='↪', callback_data='alreadyno'))
                        await call.answer('Неправильно!')
                else:
                    if correct_answer=='right':
                        cr.append(types.InlineKeyboardButton(text='↩', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='↪✅', callback_data='alreadyno'))
                        await call.answer('Правильно!')
                    else:
                        cr.append(types.InlineKeyboardButton(text='↩', callback_data='alreadyno'))
                        cr.append(types.InlineKeyboardButton(text='↪❌', callback_data='alreadyno'))
                        await call.answer('Неправильно!')
                markup.add(*cr)
                markup.add(types.InlineKeyboardButton(text='🔄 Заново', callback_data='play_plant'))
                if correct_answer=='left':
                    ans = '<i><b>↩</b>\n{0}{1}↩</i>'.format(dirn, '⚙'*amount)
                else:
                    ans = '<i><b>↪</b>\n{0}{1}↪</i>'.format(dirn, '⚙'*amount)
                if correct_answer == ansr:
                    your = '<code>Ваш ответ верен.\n💲 Награда за верный ответ: $15</code>'
                    cursor.execute('UPDATE userdata SET balance=balance+? WHERE user_id=?', (earning, a,))
                    conn.commit()
                else:
                    your = '<code>Ваш ответ неверен.\n💲 Штраф за неверный ответ: $10</code>'
                    cursor.execute('UPDATE userdata SET balance=balance-10 WHERE user_id=?', (a,))
                    conn.commit()
                cursor.execute("UPDATE userdata SET electimes=electimes+1 WHERE user_id = ?", (a,))
                conn.commit()
                msg = await main.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '<i><b>В какую сторону будет вращаться белый круг?</b>\n\nВерный ответ: {0}\n\n{1}</i>'.format(ans, your), reply_markup = markup, parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'state_balance':
            try:

            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('give_state '):
            try:
               
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('buy_metrotoken_'):
            a = int(call.data[15:])
            await buy(call, user=call.from_user, item='token', cost=metrocost, amount=a)
        if call.data.startswith('buy_traintoken_'):
            a = int(call.data[15:])
            await buy(call, user=call.from_user, item='traintoken', cost=traincost, amount=a)
        if call.data.startswith('buy_trolleytoken_'):
            a = int(call.data[17:])
            await buy(call, user=call.from_user, item='trolleytoken', cost=trolleycost, amount=a)
        if call.data == 'fight':
            try:
                a = call.from_user.id
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT battles FROM userdata WHERE user_id = ?', (a,))
                battles = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (battles,))
                onick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (battles,))
                orasa = cursor.fetchone()[0]
                if battles != 0:
                    rand = random.randint(1,10)
                    rand2 = random.randint(1,5)
                    cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                    balance = cursor.fetchone()[0]
                    cursor.execute('SELECT points FROM userdata WHERE user_id = ?', (a,))
                    points = cursor.fetchone()[0]
                    cursor.execute('UPDATE userdata SET balance = ? WHERE user_id=?', (balance+rand, a,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET points = ? WHERE user_id=?', (points+rand2, a,))
                    conn.commit()
                    await call.message.answer('<i><b><a href="tg://user?id={2}">{0}{1}</a></b> победил и получает <b>${3}</b> и <b>{4}</b> очков!</i>'.format(rasa, nick, a, rand, rand2), parse_mode = 'html')
                    await achieve(call.from_user.id, call.message.chat.id, 'firstwin')
                    rand = random.choice([0, 1, 2, 3, 4, 5])
                    if rand==3:
                        randel = random.randint(25,75)
                        cursor.execute('UPDATE userdata SET health = health-? WHERE user_id=?', (randel, battles,))
                        conn.commit()
                        cursor.execute('SELECT health FROM userdata WHERE user_id = ?', (battles,))
                        health = cursor.fetchone()[0]
                        if health<=0:
                            cursor.execute('UPDATE userdata SET prison=? WHERE user_id=?', (current_time()+600, a,))
                            conn.commit()
                            await call.message.answer('<i>&#128110; Господин <b><a href="tg://user?id={0}">{1}{2}</a></b>, вы задержаны за убийство человека в бою. Пройдёмте в отделение.\n\nВы были арестованы на <b>10 минут</b></i>'.format(a, rasa, nick), parse_mode='html')
                        await call.message.answer('&#128148; <i><b><a href="tg://user?id={2}">{0}{1}</a></b> получает серьёзную травму и теряет {3} очка здоровья :(</i>'.format(orasa, onick, battles, randel), parse_mode = 'html')
                    cursor.execute('UPDATE userdata SET battles = ? WHERE user_id=?', (0, a,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET battles = ? WHERE user_id=?', (0, battles,))
                    conn.commit()
                    now = current_time()
                    cursor.execute('UPDATE userdata SET lastfight = ? WHERE user_id=?', (now, a,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET lastfight = ? WHERE user_id=?', (now, battles,))
                    conn.commit()
                else:
                    await call.message.answer('<i><b><a href="tg://user?id={2}">{0}{1}</a></b>, так нечестно. Чтобы начать бой, напишите в ответ на сообщение пользователя <code>бой</code></i>'.format(rasa, nick, a), parse_mode = 'html')
                    return
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            try:
                await main.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
        if call.data.startswith('go_bycab_'):
            try:
                a = call.from_user.id
                station = call.data[9:]
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                place = cursor.fetchone()[0]
                if not place in CITY:
                    return
                cost = (cabcost*abs(CITY.index(place)-CITY.index(station)))//1
                if balance<cost:
                    await call.answer('❌ У вас недостаточно средств для поездки', show_alert = True)
                    return
                await call.message.answer('<i>Скоро приедем!</i>', parse_mode='html')
                try:
                    await main.delete_message(call.message.chat.id, call.message.message_id)
                except:
                    pass
                await asyncio.sleep(15)
                cursor.execute('UPDATE userdata SET place=? WHERE user_id=?', (station, a,))
                conn.commit()
                cursor.execute('UPDATE userdata SET balance=balance-? WHERE user_id=?', (cost, a,))
                conn.commit()
                await city(call.message, call.from_user.id)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('cabcost_'):
            try:
                a = call.from_user.id
                station = call.data[8:]
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                place = cursor.fetchone()[0]
                if not place in CITY:
                    return
                cost = (cabcost*abs(CITY.index(place)-CITY.index(station)))//1
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text = '🚕 Ехать', callback_data='go_bycab_{0}'.format(station)))
                markup.add(types.InlineKeyboardButton(text = '❌ Отмена', callback_data='cancel_action'))
                await call.message.answer('<i>Стоимость поездки до локации <b>{0}</b> - <b>${1}</b></i>'.format(station, cost), parse_mode='html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'cab':
            try:
                message = call.message
                a = call.from_user.id
                cursor.execute('SELECT lvl FROM userdata WHERE user_id=?', (a,))
                lvl = cursor.fetchone()[0]
                if lvl<lvlcab:
                    await call.answer('❌ Данная функция доступна только с уровня {0}'.format(lvlcab), show_alert = True)
                    return
                markup = types.InlineKeyboardMarkup(row_width=2)
                temps = []
                for temp in CITY:
                    temps.append(types.InlineKeyboardButton(text='{0}'.format(temp), callback_data='cabcost_{0}'.format(temp)))
                markup.add(*temps)
                await message.answer('<i>&#128661; Куда поедем?</i>', parse_mode='html', reply_markup=markup)
                await message.answer('<i>Стоимость поездки зависит от отдалённости места, в которое вы едете. Чтобы посмотреть цену поездки до определённого места, нажмите на него в списке локаций в предыдущем сообщении</i>'.format(cabcost), parse_mode='html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('achievements'):
            try:
                a = call.from_user.id
                achieves = ''
                for achi in ach[0]:
                    achieves += '\n\n'
                    cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(achi), (a,))
                    if cursor.fetchone()[0] > 0:
                        achieves += '&#10004; '
                    ind = ach[0].index(achi)
                    name = ach[1][ind]
                    desc = ach[2][ind]
                    achieves += '<b>{0}</b>\n<b>Задание: </b>{1}'.format(name, desc)
                    if ach[5][ind] != '':
                        cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(ach[5][ind]), (a,))
                        done = cursor.fetchone()[0]
                        achieves += '\n<b>Выполнено: </b>{0}/{1}'.format(done, ach[6][ind])
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='🔄 Обновить', callback_data='achievements_del'))
                markup.add(types.InlineKeyboardButton(text='◀ Назад', callback_data='cancel_action'))
                await call.message.answer('<i><b>&#128161; Ваши достижения</b>\nВыполненные достижения отмечены знаком &#10004;{0}</i>'.format(achieves), parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            if call.data == 'achievements_del':
                await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'set_user_mode':
            try:
                a = call.from_user.id
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT ready FROM userdata WHERE user_id = ?', (a,))
                ready = cursor.fetchone()[0]
                if ready == 1:
                    cursor.execute('UPDATE userdata SET ready = ? WHERE user_id = ?', (0,a,))
                    conn.commit()
                else:
                    cursor.execute('UPDATE userdata SET ready = ? WHERE user_id = ?', (1,a,))
                    conn.commit()
                cursor.execute('SELECT ready FROM userdata WHERE user_id = ?', (a,))
                ready = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='Изменить', callback_data='set_user_mode'))
                await main.delete_message(call.message.chat.id, call.message.message_id)
                await call.message.answer('<i><b><a href="tg://user?id={3}">{1}{2}</a></b>, ваш режим: <b>{0}</b></i>'.format('не готов' if ready == 0 else 'готов', rasa, nick, a), parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'set_user_type':
            try:
                a = call.from_user.id
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT type FROM userdata WHERE user_id = ?', (a,))
                ready = cursor.fetchone()[0]
                if ready == 'private':
                    cursor.execute('UPDATE userdata SET type = ? WHERE user_id = ?', ('public',a,))
                    conn.commit()
                else:
                    cursor.execute('UPDATE userdata SET type = ? WHERE user_id = ?', ('private',a,))
                    conn.commit()
                cursor.execute('SELECT type FROM userdata WHERE user_id = ?', (a,))
                ready = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='Изменить', callback_data='set_user_type'))
                await main.delete_message(call.message.chat.id, call.message.message_id)
                await call.message.answer('<i><b><a href="tg://user?id={3}">{1}{2}</a></b>, ваш профиль теперь <b>{0}</b></i>'.format('закрытый' if ready == 'private' else 'открытый', rasa, nick, a), parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'city':
            await city(call.message, call.from_user.id)
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'metro':
            try:
                a = call.from_user.id
                cursor.execute('SELECT token FROM userdata WHERE user_id=?', (a,))
                token = cursor.fetchone()[0]
                cursor.execute('SELECT line FROM userdata WHERE user_id=?', (a,))
                line = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                if line!=0 and line!=2:
                    markup.add(types.InlineKeyboardButton(text='🚇 Пройти на станцию', callback_data='proceed_metro'))
                else:
                    markup.add(types.InlineKeyboardButton(text='🚉 Пройти на платформу', callback_data='proceed_metro'))
                markup.add(types.InlineKeyboardButton(text='🎫 Покупка жетонов', callback_data='metro_tickets'))
                await call.message.answer('<i>У вас <b>{0}</b> жетонов</i>'.format(token), parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'trolleybus':
            try:
                a = call.from_user.id
                cursor.execute('SELECT trolleytoken FROM userdata WHERE user_id=?', (a,))
                token = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='🚏 Пройти на остановку', callback_data='proceed_trolley'))
                markup.add(types.InlineKeyboardButton(text='🎫 Покупка талонов', callback_data='trolley_tickets'))
                await call.message.answer('<i>У вас <b>{0}</b> проездных талонов</i>'.format(token), parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'proceed_metro':
            try:
                a = call.from_user.id
                cursor.execute('SELECT token FROM userdata WHERE user_id=?', (a,))
                token = cursor.fetchone()[0]
                if token<1:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='🎫 Покупка жетонов', callback_data='metro_tickets'))
                    await call.message.answer('<i>&#10060; У вас недостаточно жетонов</i>'.format(token), parse_mode='html', reply_markup=markup)
                    return
                cursor.execute('UPDATE userdata SET token=token-1 WHERE user_id=?', (a,))
                conn.commit()
                await metrocall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'forward':
            try:
                a = call.from_user.id
                cursor.execute('SELECT line FROM userdata WHERE user_id=?', (a,))
                line = cursor.fetchone()[0]
                if line==0 or line==2:
                    if not isinterval('citylines'):
                        await call.answer('Посадка ещё не началась. Поезд приедет через {0}'.format(remaining('citylines')), show_alert = True)
                        return
                else:
                    if not isinterval('metro'):
                        await call.answer('Посадка ещё не началась. Поезд приедет через {0}'.format(remaining('metro')), show_alert = True)
                        return
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                ind = metro[line].index(station)
                if line!=2 and line!=0:
                    await main.send_photo(call.message.chat.id, 'https://te.legra.ph/file/5104458f4a5bab9259a18.jpg', caption='<i>Следующая станция: <b>{0}</b>. Осторожно, двери закрываются!</i>'.format(metro[line][ind+1]), parse_mode='html')
                else:
                    await main.send_photo(call.message.chat.id, 'https://telegra.ph/file/06103228e0d120bacf852.jpg', caption='<i>Посадка завершена. Следующий остановочный пункт: <b>{0}</b></i>'.format(metro[line][ind+1]), parse_mode='html')
                await main.delete_message(call.message.chat.id, call.message.message_id)
                await asyncio.sleep(random.randint(less,more))
                await tostation(user=a, station=metro[line][ind+1])
                await metrocall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'back':
            try:
                a = call.from_user.id
                cursor.execute('SELECT line FROM userdata WHERE user_id=?', (a,))
                line = cursor.fetchone()[0]
                if line==0 or line==2:
                    if not isinterval('citylines'):
                        await call.answer('Посадка ещё не началась. Поезд приедет через {0}'.format(remaining('citylines')), show_alert = True)
                        return
                else:
                    if not isinterval('metro'):
                        await call.answer('Посадка ещё не началась. Поезд приедет через {0}'.format(remaining('metro')), show_alert = True)
                        return
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                ind = metro[line].index(station)
                if line!=2 and line!=0:
                    await main.send_photo(call.message.chat.id, 'https://te.legra.ph/file/5104458f4a5bab9259a18.jpg', caption='<i>Следующая станция: <b>{0}</b>. Осторожно, двери закрываются!</i>'.format(metro[line][ind-1]), parse_mode='html')
                else:
                    await main.send_photo(call.message.chat.id, 'https://telegra.ph/file/06103228e0d120bacf852.jpg', caption='<i>Посадка завершена. Следующий остановочный пункт: <b>{0}</b></i>'.format(metro[line][ind-1]), parse_mode='html')
                await main.delete_message(call.message.chat.id, call.message.message_id)
                await asyncio.sleep(random.randint(less, more))
                await tostation(user=a, station=metro[line][ind-1])
                await metrocall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'chats':
            await chats(call.from_user.id, call.message)
        if call.data == 'economics':
            try:
                cursor.execute("SELECT kazna FROM globaldata")
                kazna = cursor.fetchone()[0]
                cursor.execute("SELECT balance FROM clandata WHERE group_id=-1001395868701")
                balance = cursor.fetchone()[0]
                cursor.execute("SELECT lastfill FROM globaldata")
                lastfill = cursor.fetchone()[0]
                cursor.execute("SELECT coef FROM globaldata")
                coef = cursor.fetchone()[0]
                diff = current_time()-lastfill
                h = floor(diff/3600)
                m = floor(diff%3600/60)
                s = floor(diff%3600%60)
                limits = ''
                for inst in limiteds:
                    limits+='\n{0} {1} - '.format(ITEMS[0][ITEMS[1].index(inst)], ITEMS[2][ITEMS[1].index(inst)])
                    cursor.execute("SELECT {0} FROM globaldata".format(inst))
                    temp = cursor.fetchone()[0]
                    if temp<=0:
                        limits+='дефицит'
                    else:
                        limits+=str(temp)
                await call.message.answer('<i><b>&#128202; ЭКОНОМИКА ЖИВОПОЛИСА</b>\n\n&#128184; <b>Финансы</b>\n&#128176; Государственная казна - <b>${0}</b>\n&#127918; Баланс Игрового клуба - <b>${1}</b>\n\n&#127978; <b>Количество товара в Круглосуточном</b>{2}\n\n&#128666; Завоз товара в Круглосуточный осуществляется каждый день. Последний завоз был {3} часов {4} минут {5} секунд назад\n\n&#128176; <b>Центральный рынок</b>\nРыночная ставка: {6}</i>'.format(kazna, balance, limits, h, m, s, round(1/coef, 2)), parse_mode='html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'help':
            await call.message.answer('<i><b>&#10067; Справка по игре в Живополис</b>\nКоманды бота: https://telegra.ph/Komandy-ZHivopolisa-11-21\nКак играть: https://telegra.ph/Kak-igrat-v-ZHivopolis-11-21</i>', parse_mode = 'html')
        if call.data == 'transfer':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET line=? WHERE user_id=?', (transfer(a), a,))
                conn.commit()
                cursor.execute('UPDATE userdata SET place=? WHERE user_id=?', (station, a,))
                conn.commit()
                await metrocall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'airport':
            try:
                await aircall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'flight':
            try:
                if not isinterval('plane'):
                    await call.answer('Посадка ещё не началась. Самолёт прилетит через {0}'.format(remaining('plane')), show_alert = True)
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='🛫 Лететь', callback_data='flight_confirm'))
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_action'))
                await call.message.answer('<i>&#128745; Полёт на самолёте стоит <b>${0}</b>. Вы уверены, что хотите продолжить?</i>'.format(aircost), parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'flight_confirm':
            try:
                if not isinterval('plane'):
                    await call.answer('Посадка ещё не началась. Самолёт прилетит через {0}'.format(remaining('plane')), show_alert = True)
                    return
                a = call.from_user.id
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance<=aircost:
                    await call.message.answer('<i>У вас недостаточно средств :(</i>', parse_mode='html')
                    return
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET balance=balance-? WHERE user_id=?', (aircost,a,))
                conn.commit()
                tim = random.randint(lessair, moreair)
                if station == 'Аэропорт Котай':
                    await main.send_photo(call.message.chat.id, 'https://telegra.ph/file/d34459cedf14cb4b4a19a.jpg', caption='<i>Наш самолёт направляется к <b>Национальному аэропорту Живополис</b>. Путешествие займёт не более 2 минут. Удачного полёта!</i>', parse_mode = 'html')
                    dest = 'Национальный аэропорт'
                    destline = 2
                    await asyncio.sleep(tim)
                    await tostation(user=a, station=dest, line=destline)
                    await aircall(call)
                elif station == 'Национальный аэропорт':
                    await main.send_photo(call.message.chat.id, 'https://telegra.ph/file/d34459cedf14cb4b4a19a.jpg', caption='<i>Наш самолёт направляется к <b>Аэропорту Котай</b>. Путешествие займёт не более 2 минут. Удачного полёта!</i>', parse_mode = 'html')
                    dest = 'Аэропорт Котай'
                    destline = 1
                    await asyncio.sleep(tim)
                    await tostation(user=a, station=dest, line=destline)
                    await aircall(call)
                    await achieve(a, call.message.chat.id, 'flightach')
                else:
                    return
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'railway_tickets':
            try:
                markup = types.InlineKeyboardMarkup()
                a = traincost
                markup.add(types.InlineKeyboardButton(text='1 билет - ${0}'.format(a), callback_data='buy_traintoken_1'))
                markup.add(types.InlineKeyboardButton(text='5 билетов - ${0}'.format(a*5), callback_data='buy_traintoken_5'))
                markup.add(types.InlineKeyboardButton(text='10 билетов - ${0}'.format(a*10), callback_data='buy_traintoken_10'))
                markup.add(types.InlineKeyboardButton(text='20 билетов - ${0}'.format(a*20), callback_data='buy_traintoken_20'))
                markup.add(types.InlineKeyboardButton(text='50 билетов - ${0}'.format(a*50), callback_data='buy_traintoken_50'))
                markup.add(types.InlineKeyboardButton(text='◀ Назад', callback_data='cancel_action'))
                await call.message.answer('<i>Сколько билетов вы хотите купить?\nТариф <b>Железная дорога</b></i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'metro_tickets':
            try:
                markup = types.InlineKeyboardMarkup()
                a = metrocost
                markup.add(types.InlineKeyboardButton(text='1 жетон - ${0}'.format(a), callback_data='buy_metrotoken_1'))
                markup.add(types.InlineKeyboardButton(text='5 жетонов - ${0}'.format(a*5), callback_data='buy_metrotoken_5'))
                markup.add(types.InlineKeyboardButton(text='10 жетонов - ${0}'.format(a*10), callback_data='buy_metrotoken_10'))
                markup.add(types.InlineKeyboardButton(text='20 жетонов - ${0}'.format(a*20), callback_data='buy_metrotoken_20'))
                markup.add(types.InlineKeyboardButton(text='50 жетонов - ${0}'.format(a*50), callback_data='buy_metrotoken_50'))
                markup.add(types.InlineKeyboardButton(text='◀ Назад', callback_data='cancel_action'))
                await call.message.answer('<i>Сколько жетонов вы хотите купить?\nТариф <b>Метро и городская электричка</b></i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'trolley_tickets':
            try:
                markup = types.InlineKeyboardMarkup()
                a = metrocost
                markup.add(types.InlineKeyboardButton(text='1 талон - ${0}'.format(a), callback_data='buy_trolleytoken_1'))
                markup.add(types.InlineKeyboardButton(text='5 талонов - ${0}'.format(a*5), callback_data='buy_trolleytoken_5'))
                markup.add(types.InlineKeyboardButton(text='10 талонов - ${0}'.format(a*10), callback_data='buy_trolleytoken_10'))
                markup.add(types.InlineKeyboardButton(text='20 талонов - ${0}'.format(a*20), callback_data='buy_trolleytoken_20'))
                markup.add(types.InlineKeyboardButton(text='50 талонов - ${0}'.format(a*50), callback_data='buy_trolleytoken_50'))
                markup.add(types.InlineKeyboardButton(text='◀ Назад', callback_data='cancel_action'))
                await call.message.answer('<i>Сколько талонов вы хотите купить?\nТариф <b>Троллейбус</b></i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'tickets':
            try:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='🚇 Метро и городская электричка', callback_data='metro_tickets'))
                markup.add(types.InlineKeyboardButton(text='🚆 Железная дорога', callback_data='railway_tickets'))
                markup.add(types.InlineKeyboardButton(text='🚎 Троллейбус', callback_data='trolley_tickets'))
                markup.add(types.InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))
                await call.message.answer('<i>Выберите тариф</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'railway_station':
            try:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='💺 Зал ожидания', callback_data='lounge'))
                markup.add(types.InlineKeyboardButton(text='🎫 Билетные кассы', callback_data='tickets'))
                markup.add(types.InlineKeyboardButton(text='🍔 Кафетерий "Енот Кебаб"', callback_data='enot_kebab'))
                await call.message.answer('<i>Пора уже валить отсюда...</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'bus':
            try:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='🚌 К платформам', callback_data='bus_lounge'))
                markup.add(types.InlineKeyboardButton(text='🎫 Билетные кассы', callback_data='tickets'))
                markup.add(types.InlineKeyboardButton(text='🍔 Кафетерий "Енот Кебаб"', callback_data='enot_kebab'))
                await call.message.answer('<i>Пора уже валить отсюда...</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'lounge':
            try:
                await traincall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'bus_lounge':
            try:
                await regbuscall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'work':
            try:
                await work(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'salary':
            try:
                await ask(call.from_user.id, call.message)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('train_'):
            try:
                if not isinterval('train'):
                    await call.answer('Посадка ещё не началась. Поезд приедет через {0}'.format(remaining('train')), show_alert = True)
                    return
                a = call.from_user.id
                st = call.data[6:]
                cursor.execute('SELECT traintoken FROM userdata WHERE user_id=?', (a,))
                traintoken = cursor.fetchone()[0]
                if traintoken<1:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='🎫 Покупка билетов', callback_data='tickets'))
                    await call.message.answer('<i>&#10060; У вас нет билета</i>', parse_mode='html', reply_markup=markup)
                    return
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET traintoken=traintoken-1 WHERE user_id=?', (a,))
                tim = random.randint(lesstrain, moretrain)
                name = trains[2][trains[0].index(st)]
                await main.delete_message(call.message.chat.id, call.message.message_id)
                await main.send_photo(call.message.chat.id, 'https://telegra.ph/file/ead2a4bfc5e78cf56ba1e.jpg', caption='🚆 <i>Наш поезд отправляется на станцию <b>{0}</b>. Путешествие займёт не больше минуты. Удачной поездки!</i>'.format(name), parse_mode = 'html')
                await asyncio.sleep(tim)
                await tostation(user=a, station=st)
                await traincall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('walk_'):
            try:
                a = call.from_user.id
                message = call.message
                name = call.data[5:]
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                exists = False
                index = 0
                for wlk in walk:
                    if station in wlk:
                        exists = True
                        index = wlk.index(station)
                if not exists:
                    return
                exists = False
                for wlk in walk:
                    if wlk[index] == name:
                        exists = True
                if not exists:
                    return
                tim = walks[index]
                await call.message.answer('🚶 <i>Как же хорошо пройтись пешочком. Путешествие до места <b>{0}</b> займёт около {1} секунд. Удачного путешествия!</i>'.format(name, tim), parse_mode = 'html')
                await asyncio.sleep(tim)
                await tostation(user=a, station=name)
                cursor.execute('UPDATE userdata SET walk=walk+1 WHERE user_id=?', (a,))
                conn.commit()
                cursor.execute("SELECT walk FROM userdata WHERE user_id=?", (a,))
                walked = cursor.fetchone()[0]
                if walked>=20:
                    await achieve(a, call.message.chat.id, 'walkach')
                await city(message, a)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('gobus_'):
            try:
                if not isinterval('taxi'):
                    await call.answer('Посадка ещё не началась. Маршрутка приедет через {0}'.format(remaining('taxi')), show_alert = True)
                    return
                a = call.from_user.id
                name = call.data[6:]
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance<buscost:
                    markup = types.InlineKeyboardMarkup()
                    await call.message.answer('<i>&#10060; У вас нет достаточно денег</i>', parse_mode='html', reply_markup=markup)
                    return
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET balance=balance-? WHERE user_id=?', (buscost,a,))
                tim = random.randint(lesstrain, moretrain)
                await main.send_photo(call.message.chat.id, 'https://telegra.ph/file/8da21dc03e8f266e0845a.jpg', caption='🚐 <i>Посадка завершена. Следующая остановка: <b>{0}</b>. Путешествие займёт не больше минуты. Удачной поездки!</i>'.format(name), parse_mode = 'html')
                await main.delete_message(call.message.chat.id, call.message.message_id)
                await asyncio.sleep(tim)
                await tostation(user=a, station=name)
                await regbuscall(call)
                await achieve(a, call.message.chat.id, 'busride')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('goreg_'):
            try:
                if not isinterval('bus'):
                    await call.answer('Посадка ещё не началась. Автобус приедет через {0}'.format(remaining('bus')), show_alert = True)
                    return
                a = call.from_user.id
                name = call.data[6:]
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                if balance<regbuscost:
                    markup = types.InlineKeyboardMarkup()
                    await call.message.answer('<i>&#10060; У вас нет достаточно денег</i>', parse_mode='html', reply_markup=markup)
                    return
                cursor.execute('SELECT place FROM userdata WHERE user_id=?', (a,))
                station = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET balance=balance-? WHERE user_id=?', (regbuscost,a,))
                tim = random.randint(lesstrain, moretrain)
                await main.send_photo(call.message.chat.id, 'https://telegra.ph/file/34226b77d11cbd7e19b7b.jpg', caption='🚌 <i>Посадка завершена. Следующая остановка: <b>{0}</b>. Путешествие займёт не больше минуты. Удачной поездки!</i>'.format(name), parse_mode = 'html')
                await main.delete_message(call.message.chat.id, call.message.message_id)
                await asyncio.sleep(tim)
                await tostation(user=a, station=name)
                await regbuscall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('paybill '):
            try:
                a = call.from_user.id
                money = int(call.data.split(" ")[1])
                ownerid = int(call.data.split(" ")[2])
                if ownerid==a:
                    if call.message!=None:
                        await main.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '<i>Счёт отменён</i>', parse_mode = 'html')
                    else:
                        await main.edit_message_text(inline_message_id = call.inline_message_id, text = '<i>Счёт отменён</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (ownerid,))
                balance2 = cursor.fetchone()[0]
                if balance<money:
                    await call.answer(text='❌ У вас недостаточно средств', show_alert = True)
                    return
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET balance = ? WHERE user_id=?', (balance-money, a,))
                conn.commit()
                cursor.execute('UPDATE userdata SET balance = ? WHERE user_id=?', (balance2+money, ownerid,))
                conn.commit()
                await call.answer(text='✅ Вы оплатили счёт', show_alert = True)
                try:
                    await main.send_message(ownerid, text = '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> оплатил счёт <b>${2}</b></i>'.format(rasa, nick, money, a), parse_mode = 'html')
                except:
                    if call.message!=None:
                        await call.message.reply('<i><b><a href="tg://user?id={3}">{0}{1}</a></b> оплатил счёт <b>${2}</b></i>'.format(rasa, nick, money, a), parse_mode = 'html')
                    else:
                        await main.edit_message_text(inline_message_id = call.inline_message_id, text = '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> оплатил счёт <b>${2}</b></i>'.format(rasa, nick, money, a), parse_mode = 'html')
                if money>0:
                    await main.send_message(fid, text = '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> оплатил счёт <b>${2}</b>\n#user_getcheck</i>'.format(rasa, nick, money, a), parse_mode = 'html')
            except Exception as e:
                try:
                    await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                    await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
                except:
                    await main.edit_message_text(inline_message_id = call.inline_message_id, text = '<i><b>Ошибка: </b>{0}</i>'.format(e), parse_mode='html')
        if call.data == 'cancel_process':
            try:
                a = call.from_user.id
                await main.delete_message(call.message.chat.id, call.message.message_id)
                cursor.execute('UPDATE userdata SET process = ? WHERE user_id=?', ('nothing', a,))
                conn.commit()
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('slot '):
            try:
                a = call.from_user.id
                arr = call.data.split(' ')
                oth = arr[3]
                item = arr[1]
                cost = int(arr[2])
                if a==int(oth):
                    if call.message != None:
                        await main.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '<i>Слот отменён продавцом</i>', parse_mode = 'html')
                    else:
                        await main.edit_message_text(inline_message_id=call.inline_message_id, text = '<i>Слот отменён продавцом</i>', parse_mode = 'html')
                    cursor.execute('UPDATE userdata SET {0} = {0}+1 WHERE user_id=?'.format(item), (a,))
                    conn.commit()
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT balance FROM userdata WHERE user_id=?', (oth,))
                obalance = cursor.fetchone()[0]
                if balance<cost:
                    await call.answer('❌ У вас недостаточно средств', show_alert = True)
                    return
                cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(item), (a,))
                ims = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET {0} = ? WHERE user_id=?'.format(item), (ims+1, a,))
                cursor.execute('UPDATE userdata SET balance = ? WHERE user_id=?', (balance-cost, a,))
                cursor.execute('UPDATE userdata SET balance = ? WHERE user_id=?', (obalance+cost, oth,))
                conn.commit()
                ind = ITEMS[1].index(item)
                itm = ITEMS[0][ind]+' '+ITEMS[2][ind]
                try:
                    await main.send_message(oth, '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> купил у вас <b>{2}</b> за <b>${4}</b></i>'.format(rasa, nick, itm, a, cost), parse_mode = 'html')
                except:
                    pass
                if cost>0:
                    await main.send_message(fid, '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> купил <b>{2}</b> за <b>${4}</b>\n#user_getitem</i>'.format(rasa, nick, itm, a, cost), parse_mode = 'html')
                try:
                    await main.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> купил <b>{2}</b> за <b>${4}</b></i>'.format(rasa, nick, itm, a, cost), parse_mode = 'html')
                except:
                    await main.edit_message_text(inline_message_id = call.inline_message_id, text = '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> купил <b>{2}</b> за <b>${4}</b></i>'.format(rasa, nick, itm, a, cost), parse_mode = 'html')
                await call.answer("Спасибо за покупку", show_alert=True)
            except Exception as e:
                if call.message!=None:
                    await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                    await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
                else:
                    await main.edit_message_text(inline_message_id = call.inline_message_id, text = '<i><b>Ошибка: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'create_clan':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Создать клан может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                chn = call.message.chat.title
                if count == 0:
                    cursor.execute('INSERT INTO clandata (name, group_id, owner_id, username, hqplace) VALUES (?, ?, ?, ?, ?)', (chn, chid, a, '', ''))
                    conn.commit()
                    await startdef(call.message)
                    cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                    rasa = cursor.fetchone()[0]
                    cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                    nick = cursor.fetchone()[0]
                    await main.send_message(fid, '<i><b><a href="tg://user?id={0}">{1}{2}</a></b> создал клан <b>{3} ({4})</b>\n#clan_create</i>'.format(a, rasa, nick, chn, chid), parse_mode='html')
                else:
                    await main.send_message(chid, '<i>&#10060; Клан уже существует</i>', parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'join_clan':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
                nick = cursor.fetchone()[0]
                chn = call.message.chat.title
                if count == 0:
                    return
                cursor.execute('SELECT type FROM clandata WHERE group_id=?', (chid,))
                cursor.execute('SELECT clan FROM userdata WHERE user_id=?', (a,))
                if cursor.fetchone()[0]!=chid:
                    cursor.execute('UPDATE userdata SET clan=? WHERE user_id=?', (chid, a,))
                    cursor.execute('UPDATE userdata SET clanname=? WHERE user_id=?', (chn, a,))
                    conn.commit()
                    await main.send_message(chid, '<i><b><a href="tg://user?id={2}">{0}{1}</a></b> присоединился к клану</i>'.format(rasa, nick, a), parse_mode = 'html')
                else:
                    cursor.execute('UPDATE userdata SET clan=? WHERE user_id=?', (0, a,))
                    cursor.execute('UPDATE userdata SET clanname=? WHERE user_id=?', ('', a,))
                    conn.commit()
                    await main.send_message(chid, '<i><b><a href="tg://user?id={2}">{0}{1}</a></b> вышел из клана</i>'.format(rasa, nick, a), parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'call_clan':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM userdata WHERE clan = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT name FROM clandata WHERE group_id = ?', (chid,))
                chn = cursor.fetchone()[0]
                cursor.execute('SELECT username FROM clandata WHERE group_id = ?', (chid,))
                chu = cursor.fetchone()[0]
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Созвать клан может только администратор чата</i>', parse_mode = 'html')
                    return
                if count == 0:
                    await call.answer(text='В клане никого нет :(')
                    return
                cursor.execute('SELECT * FROM userdata WHERE clan = ?', (chid,))
                err = 0
                nerr = 0
                for row in cursor:
                    try:
                        await main.send_message(row[1], '<i>Клан <b><a href="{1}">{0}</a></b> созывает вас</i>'.format(chn, chu), parse_mode = 'html')
                        nerr+=1
                    except:
                        err+=1
                await call.message.answer('<i><b>&#128227; Рассылка завершена</b>\n&#9989; Удачно: {0}\n&#10060; Ошибки: {1}</i>'.format(nerr, err), parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clan_members':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                chu = call.message.chat.username
                cursor.execute('SELECT count(*) FROM userdata WHERE clan = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT owner_id FROM clandata WHERE group_id = ?', (chid,))
                ownerid = cursor.fetchone()[0]
                cursor.execute('SELECT * FROM userdata WHERE user_id = ?', (ownerid,))
                owner = cursor.fetchone()
                try:
                    parts = '\n&#128081; <b>Создатель клана: \n<a href="tg://user?id={2}">{0}{1}</a></b>\n\n&#128101; Участники клана:'.format(owner[9], owner[7], owner[1])
                except:
                    parts = '&#128101; Участники клана:'
                cursor.execute('SELECT * FROM userdata WHERE clan = ?', (chid,))
                for row in cursor:
                    parts = parts+'\n<a href="tg://user?id={0}">{1}{2}</a>'.format(row[1], row[9], row[7])
                await main.send_message(chid, '<i><b>{0}</b></i>'.format(parts), parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clan_settings':
            await clancall(call)
        if call.data == 'clan_settings2':
            await main.delete_message(call.message.chat.id, call.message.message_id)
            await clancall(call)
        if call.data == 'clan_profile':
            await main.delete_message(call.message.chat.id, call.message.message_id)
            await clanprof(call)
        if call.data == 'cancel_action2':
            try:
                await startdef(call.message)
            except:
                pass
            await main.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == 'clan_type':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT lvl FROM userdata WHERE user_id=?', (a,))
                lvl = cursor.fetchone()[0]
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Управлять кланом может только администратор чата</i>', parse_mode = 'html')
                    return
                typ = ''
                if call.message.chat.username is None:
                    thischat = await main.get_chat(chid)
                    chu = thischat.invite_link
                else:
                    chu = 't.me/'+call.message.chat.username
                cursor.execute('SELECT type FROM clandata WHERE group_id=?', (chid,))
                if cursor.fetchone()[0] == 'private':
                    if lvl<lvlclan:
                        await call.answer('❌ Данная функция доступна только с уровня {0}'.format(lvlclan), show_alert = True)
                        return
                    cursor.execute('UPDATE clandata SET type=? WHERE group_id=?', ('public', chid,))
                    cursor.execute('UPDATE clandata SET username=? WHERE group_id=?', (chu, chid,))
                    conn.commit()
                else:
                    cursor.execute('UPDATE clandata SET type=? WHERE group_id=?', ('private', chid,))
                    cursor.execute('UPDATE clandata SET username=? WHERE group_id=?', (chu, chid,))
                    conn.commit()
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            await main.delete_message(call.message.chat.id, call.message.message_id)
            await clancall(call)
        if call.data == 'clan_notifications':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Управлять кланом может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT notif FROM clandata WHERE group_id=?', (chid,))
                if cursor.fetchone()[0] == 1:
                    cursor.execute('UPDATE clandata SET notif=0 WHERE group_id=?', (chid,))
                    conn.commit()
                else:
                    cursor.execute('UPDATE clandata SET notif=1 WHERE group_id=?', (chid,))
                    conn.commit()
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
            await main.delete_message(call.message.chat.id, call.message.message_id)
            await clancall(call)
        if call.data == 'set_user_nick':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('setnick', a,))
                conn.commit()
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_process'))
                await main.send_message(chid, '<i>Введите новый ник</i>', parse_mode='html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'set_user_photo':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('setphoto', a,))
                conn.commit()
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_process'))
                markup.add(types.InlineKeyboardButton(text='🗑 Удалить', callback_data='clear_user_photo'))
                await main.send_message(chid, '<i>Отправьте ссылку на фото или само фото</i>', parse_mode='html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clear_user_photo':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
                cursor.execute('UPDATE userdata SET photo="" WHERE user_id=?', (a,))
                conn.commit()
                await main.send_message(chid, '<i>Фото удалено</i>', parse_mode='html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'hq_number':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('seekhouse', a,))
                conn.commit()
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_process'))
                await main.send_message(chid, '<i>Введите номер дома</i>', parse_mode='html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'set_user_key':
            try:
                if call.message.chat.type!='private':
                    await main.send_message(chid, '<i>В целях обеспечения конфиденциальности пользователей эта команда работает только в личных сообщениях с ботом. Откройте настройки в ЛС с ботом и введите ключ доступа</i>', parse_mode='html')
                    cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                    conn.commit()
                    return
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('setkey', a,))
                conn.commit()
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_process'))
                await main.send_message(chid, '<i>Введите новый ключ доступа</i>', parse_mode='html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'log_in':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('login', a,))
                conn.commit()
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_process'))
                await main.send_message(chid, '<i>Введите ключ доступа</i>', parse_mode='html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'proceed_trolley':
            try:
                a = call.from_user.id
                cursor.execute('SELECT trolleytoken FROM userdata WHERE user_id=?', (a,))
                token = cursor.fetchone()[0]
                if token<1:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text='🎫 Покупка талонов', callback_data='trolley_tickets'))
                    await call.message.answer('<i>&#10060; У вас недостаточно проездных талонов</i>'.format(token), parse_mode='html', reply_markup=markup)
                    return
                cursor.execute('UPDATE userdata SET trolleytoken=trolleytoken-1 WHERE user_id=?', (a,))
                conn.commit()
                await buscall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clan_link':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Изменять настройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('clanuser', a,))
                conn.commit()
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_process'))
                await main.send_message(chid, '<i>Введите новую ссылку клана. Ссылка на чат должна начинаться с <code>https://t.me/</code> или <code>t.me/</code>.\nРазрешено указывать ссылку на пользователя Telegram (при разрешении этого пользователя), некоммерческий канала или бот, связанный с игрой. Указывать ссылку на коммерческие или не связанные с игрой боты, группы и каналы запрещено</i>', parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'delete_clan':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                cursor.execute('SELECT owner_id FROM clandata WHERE group_id=?', (chid,))
                if a != cursor.fetchone()[0]:
                    await main.send_message(chid, '&#10060; <i>Распустить клан может только его создатель</i>', parse_mode = 'html')
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text = '✅ Подтвердить роспуск', callback_data = 'delete_clan_confirm'))
                markup.add(types.InlineKeyboardButton(text = '❌ Отменить', callback_data = 'cancel_action'))
                await call.message.answer('<i>Вы уверены, что хотите распустить клан? Это действие отменить нельзя</i>', parse_mode = 'html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'delete_clan_confirm':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                cursor.execute('SELECT owner_id FROM clandata WHERE group_id=?', (chid,))
                if a != cursor.fetchone()[0]:
                    await main.send_message(chid, '&#10060; <i>Распустить клан может только его создатель</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('SELECT name FROM clandata WHERE group_id=?', (chid,))
                chn = cursor.fetchone()[0]
                await main.send_message(fid, '<i><b><a href="tg://user?id={0}">{1}{2}</a></b> распустил клан <b>{3} ({4})</b>\n#clan_delete</i>'.format(a, rasa, nick, chn, chid), parse_mode='html')
                cursor.execute('DELETE FROM clandata WHERE group_id = ?', (chid,))
                conn.commit()
                await call.message.answer('<i>Клан успешно распущен</i>', parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'headquarters':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Создать штаб-квартиру клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT place FROM userdata WHERE user_id = ?', (a,))
                place = cursor.fetchone()[0]
                cursor.execute('SELECT hqplace FROM clandata WHERE group_id=?', (chid,))
                hqplace = cursor.fetchone()[0]
                if hqplace!=None and hqplace!='':
                    await main.send_message(chid, '<i>У клана уже есть штаб-квартира</i>', parse_mode='html')
                    return
                cursor.execute('UPDATE clandata SET hqplace=? WHERE group_id=?', (place, chid,))
                conn.commit()
                cursor.execute('SELECT hqplace FROM clandata WHERE group_id=?', (chid,))
                hqplace = cursor.fetchone()[0]
                try:
                    cursor.execute('SELECT MAX(address) FROM clandata WHERE hqplace=?', (hqplace,))
                    address = cursor.fetchone()[0]+1
                except:
                    address = 1
                cursor.execute('UPDATE clandata SET address=? WHERE group_id=?', (address, chid,))
                conn.commit()
                cursor.execute('SELECT address FROM clandata WHERE group_id=?', (chid,))
                address = cursor.fetchone()[0]
                await main.send_message(chid, '<i>&#127970; Готово! Теперь адрес штаб-квартиры клана: <b>{0}, {1}</b></i>'.format(hqplace, address), parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clan_buildings':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                cursor.execute('SELECT lootbox FROM clandata WHERE group_id = ?', (chid,))
                lootbox = cursor.fetchone()[0]
                cursor.execute('SELECT foodshop FROM clandata WHERE group_id = ?', (chid,))
                foodshop = cursor.fetchone()[0]
                cursor.execute('SELECT apteka FROM clandata WHERE group_id = ?', (chid,))
                apteka = cursor.fetchone()[0]
                cursor.execute('SELECT farm FROM clandata WHERE group_id = ?', (chid,))
                farm = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                if lootbox>=1:
                    markup.add(types.InlineKeyboardButton(text='🏤 Почтовое отделение', callback_data='mailoffice'))
                if foodshop>=1:
                    markup.add(types.InlineKeyboardButton(text='🍵 Столовая', callback_data='canteen'))
                if apteka>=1:
                    markup.add(types.InlineKeyboardButton(text='💊 Аптека', callback_data='chemists'))
                if farm>=1:
                    markup.add(types.InlineKeyboardButton(text='🐄 Ферма', callback_data='clan_farm'))
                markup.add(types.InlineKeyboardButton(text='🏗 Строительное агенство', callback_data='building_shop'))
                await main.send_message(chid, '<i>&#127959; <b>Постройки </b>- один из самых интересных способов разнообразить клан</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'building_shop':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Управлять постройками клана может только администратор чата</i>', parse_mode = 'html')
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='🏤 Почтовое отделение', callback_data='mailoffice'))
                markup.add(types.InlineKeyboardButton(text='🍵 Столовая', callback_data='canteen'))
                markup.add(types.InlineKeyboardButton(text='💊 Аптека', callback_data='chemists'))
                markup.add(types.InlineKeyboardButton(text='🐄 Ферма', callback_data='clan_farm'))
                await main.send_message(chid, '<i>&#127959; <b>Постройки </b>- один из самых интересных способов разнообразить клан</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clan_plugins':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Управлять дополнениями клана может только администратор чата</i>', parse_mode = 'html')
                    return
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='📛 Фильтр сообщений', callback_data='clanfilter'))
                markup.add(types.InlineKeyboardButton(text='🎰 Мини-казино', callback_data='clangameclub'))
                await main.send_message(chid, '<i>➕ <b>Дополнения</b> - способы улучшить клан</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clanfilter':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Управлять дополнениями клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT stickers FROM clandata WHERE group_id = ?', (chid,))
                stickers = cursor.fetchone()[0]
                cursor.execute('SELECT dice FROM clandata WHERE group_id = ?', (chid,))
                dice = cursor.fetchone()[0]
                cursor.execute('SELECT mat FROM clandata WHERE group_id = ?', (chid,))
                mat = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='🀄 Стикеры: {0}'.format('Запрещены' if stickers==0 else 'Разрешены'), callback_data='clanfset_stickers'))
                markup.add(types.InlineKeyboardButton(text='🎲 Игровые эмодзи: {0}'.format('Запрещены' if dice==0 else 'Разрешены'), callback_data='clanfset_dice'))
                markup.add(types.InlineKeyboardButton(text='🤬 Бранные слова: {0}'.format('Запрещены' if mat==0 else 'Разрешены'), callback_data='clanfset_mat'))
                await main.send_message(chid, '<i>📛 <b>Фильтр сообщений</b> - отличный способ навести порядок в клане. Бот будет удалять сообщения, которые не соответствуют требованиям фильтра</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('clanfset_'):
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                set = call.data[9:]
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Управлять дополнениями клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT {0} FROM clandata WHERE group_id = ?'.format(set), (chid,))
                stickers = cursor.fetchone()[0]
                s = 1 if stickers==0 else 0
                cursor.execute('UPDATE clandata SET {0}=? WHERE group_id = ?'.format(set), (s,chid,))
                conn.commit()
                await clancall(call)
                await main.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clangameclub':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Управлять дополнениями клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT gameclub FROM clandata WHERE group_id = ?', (chid,))
                gameclub = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                if gameclub==1:
                    txt = '📳 Включить - $700'
                else:
                    txt = '📴 Выключить (возврат $700)'
                markup.add(types.InlineKeyboardButton(text=txt, callback_data='buy_gameclub'))
                await main.send_message(chid, '<i>🎰 <b>Мини-казино</b> даёт пользователям возможность играть в игровые автоматы. Условия:\n1. 50% денег за каждую крутку идёт на баланс клана, 50% отдаётся Игровому клубу.\n2. Деньги за выигрыши вычитаются из баланса клана. При нехватке денег на балансе клана из казны забирается удвоенная сумма выигрыша, в Игровой клуб отдаётся сумма выигрыша. При нехватке денег в казне пользователь не может получить выигрыш.\n3. Услугу "Мини-казино" можно отменить, при этом отменившему админу возвращается оплаченная при покупке сумма.</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clanlocation':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Управлять настройками клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT islocation FROM clandata WHERE group_id = ?', (chid,))
                loc = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                if loc==0:
                    txt = '📳 Включить - $1200'
                else:
                    txt = '📴 Выключить (возврат $1200)'
                markup.add(types.InlineKeyboardButton(text=txt, callback_data='buy_location'))
                await main.send_message(chid, '<i>При включённом режиме 🏛 <b>Локации</b> клан будет показываться в списке локаций местности, в которой размещена штаб-квартира. Клан при этом должен быть публичным и иметь штаб-квартиру.\nПостройка локации стоит $1200, при её отмене отменившему администратору возвращается эта сумма</i>', parse_mode='html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'buy_location':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                cursor.execute('SELECT islocation FROM clandata WHERE group_id = ?', (chid,))
                loc = cursor.fetchone()[0]
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Покупать и продавать постройки для клана может только администратор чата</i>', parse_mode = 'html')
                    return
                if loc == 0:
                    cursor.execute('SELECT type FROM clandata WHERE group_id = ?', (chid,))
                    type = cursor.fetchone()[0]
                    cursor.execute('SELECT hqplace FROM clandata WHERE group_id = ?', (chid,))
                    hqplace = cursor.fetchone()[0]
                    if hqplace=='' or type=='private':
                        await call.answer('❌ Только публичные кланы с штаб-квартирами могут иметь свою локацию', show_alert=True)
                        return
                    if balance>=1200:
                        cursor.execute('UPDATE clandata SET islocation=1 WHERE group_id=?', (chid,))
                        conn.commit()
                        cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance-1200, a,))
                        conn.commit()
                        await clancall(call)
                    else:
                        await call.answer('❌ У вас недостаточно средств', show_alert = True)
                        return
                else:
                    if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                        await main.send_message(chid, '&#10060; <i>Покупать постройки для клана может только администратор чата</i>', parse_mode = 'html')
                        return
                    cursor.execute('UPDATE clandata SET islocation=0 WHERE group_id=?', (chid,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance+1200, a,))
                    conn.commit()
                    await call.answer('Успех!', show_alert = True)
                    await clancall(call)
                await main.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'buy_gameclub':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                cursor.execute('SELECT gameclub FROM clandata WHERE group_id = ?', (chid,))
                gameclub = cursor.fetchone()[0]
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Покупать и продавать постройки для клана может только администратор чата</i>', parse_mode = 'html')
                    return
                if gameclub == 1:
                    if balance>=700:
                        cursor.execute('UPDATE clandata SET gameclub=? WHERE group_id=?', (0, chid,))
                        conn.commit()
                        cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance-700, a,))
                        conn.commit()
                        await clancall(call)
                    else:
                        await call.answer('❌ У вас недостаточно средств', show_alert = True)
                        return
                else:
                    if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                        await main.send_message(chid, '&#10060; <i>Покупать постройки для клана может только администратор чата</i>', parse_mode = 'html')
                        return
                    cursor.execute('UPDATE clandata SET gameclub=? WHERE group_id=?', (1, chid,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance+700, a,))
                    conn.commit()
                    await call.answer('Успех!', show_alert = True)
                    await clancall(call)
                await main.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'buy_mailoffice':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT lootbox FROM clandata WHERE group_id = ?', (chid,))
                lootbox = cursor.fetchone()[0]
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Покупать постройки для клана может только администратор чата</i>', parse_mode = 'html')
                    return
                if balance>=700:
                    cursor.execute('UPDATE clandata SET lootbox=? WHERE group_id=?', (lootbox+1, chid))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance-700*lootbox, a))
                    conn.commit()
                    await clancall(call)
                else:
                    await call.answer('❌ У вас недостаточно средств', show_alert = True)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'act_mailoffice':
            try:
                a = call.from_user.id
                now = datetime.now()
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT lootbox FROM clandata WHERE group_id = ?', (chid,))
                lootbox = cursor.fetchone()[0]
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT lastbox FROM clandata WHERE group_id = ?', (chid,))
                box = cursor.fetchone()[0]
                cursor.execute('SELECT name FROM clandata WHERE group_id = ?', (chid,))
                chn = cursor.fetchone()[0]
                cursor.execute('SELECT username FROM clandata WHERE group_id = ?', (chid,))
                chu = cursor.fetchone()[0]
                diff = (now - datetime.fromtimestamp(0)).total_seconds() - box
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Раздавать лутбоксы для клана может только администратор чата</i>', parse_mode = 'html')
                    return
                if lootbox==0:
                    await main.send_message(chid, '<i>&#10060; В клане нет постройки <b>"Почтовое отделение"</b></i>', parse_mode='html')
                    return
                if diff>=604800:
                    cursor.execute('SELECT * FROM userdata WHERE clan=?', (chid,))
                    err = 0
                    nerr = 0
                    for row in cursor:
                        try:
                            await main.send_message(row[1], '<i>Клан <b><a href="{1}">{0}</a></b> дарит вам {2} &#128230;<b>Лутбокс</b></i>'.format(chn, chu, lootbox), parse_mode = 'html')
                            nerr+=1
                        except:
                            err+=1
                    conn.commit()
                    await call.message.answer('<i><b>📦 Рассылка лутбоксов завершена</b>\n&#9989; Удачно: {0}\n&#10060; Ошибки: {1}</i>'.format(nerr, err), parse_mode = 'html')
                    cursor.execute('UPDATE userdata SET lootbox=lootbox+? WHERE clan=?', (lootbox, chid,))
                    cursor.execute('UPDATE clandata SET lastbox = ? WHERE group_id = ?', ((now - datetime.fromtimestamp(0)).total_seconds(), chid,))
                    conn.commit()
                else:
                    d = 7-ceil(diff/86400)
                    h = 24-ceil(diff%86400/3600)
                    m = 60-ceil(diff%86400%3600/60)
                    s = 60-ceil(diff%86400%3600%60)
                    await main.send_message(chid, f'<i>Следующий лутбокс ожидается через {d} дней {h} часов {m} минут {s} секунд</i>', parse_mode='html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'mailoffice':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT lootbox FROM clandata WHERE group_id = ?', (chid,))
                lootbox = cursor.fetchone()[0]
                if count == 0:
                    return
                markup = types.InlineKeyboardMarkup()
                lvl = ''
                if lootbox >=1:
                    markup.add(types.InlineKeyboardButton(text='📦 Раздать лутбоксы', callback_data='act_mailoffice'))
                    markup.add(types.InlineKeyboardButton(text='🏤 Прокачка - ${0}'.format(700*lootbox), callback_data='buy_mailoffice'))
                    markup.add(types.InlineKeyboardButton(text='💸 Продать постройку (возврат $700)', callback_data='sell_mailoffice'))
                    lvl = 'Уровень вашего почтового отделения: <b>{0}</b>'.format(lootbox)
                else:
                    markup.add(types.InlineKeyboardButton(text='🏤 Купить - $700', callback_data='buy_mailoffice'))
                    lvl = 'У вас нет почтового отделения'
                await main.send_message(chid, '<i>&#127972; <b>Почтовое отделение</b> - полезная постройка для раздачи лутбоксов соклановцам. {0}</i>'.format(lvl), parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clan_farm':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT farm FROM clandata WHERE group_id = ?', (chid,))
                farm = cursor.fetchone()[0]
                cursor.execute('SELECT cow FROM clandata WHERE group_id = ?', (chid,))
                cow = cursor.fetchone()[0]
                cursor.execute('SELECT cow FROM userdata WHERE user_id = ?', (a,))
                my_cow = cursor.fetchone()[0]
                if count == 0:
                    return
                markup = types.InlineKeyboardMarkup()
                if farm >=1:
                    markup.add(types.InlineKeyboardButton(text='🐄 Пожертвовать корову', callback_data='donate_cow'))
                    markup.add(types.InlineKeyboardButton(text='🥛 Подоить корову', callback_data='milk_clan'))
                    markup.add(types.InlineKeyboardButton(text='💸 Продать постройку (возврат $500)', callback_data='sell_farm'))
                    lvl = '&#128004; В клане <b>{0}</b> коров. У вас <b>{1}</b> коров'.format(cow, my_cow)
                else:
                    markup.add(types.InlineKeyboardButton(text='🐄 Купить - $500', callback_data='buy_farm'))
                    lvl = 'В клане нет фермы'
                await main.send_message(chid, '<i>&#128004; <b>Ферма</b> - отличный способ получить молоко в клане. Доить коров можно раз в день.\n{0}</i>'.format(lvl), parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'sell_canteen':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT foodshop FROM clandata WHERE group_id = ?', (chid,))
                foodshop = cursor.fetchone()[0]
                if foodshop<1:
                    await main.send_message(chid, '<i>В клане нет столовой</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Продавать постройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE clandata SET foodshop=? WHERE group_id=?', (0, chid))
                conn.commit()
                cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance+500, a))
                conn.commit()
                await clancall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'sell_farm':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT farm FROM clandata WHERE group_id = ?', (chid,))
                foodshop = cursor.fetchone()[0]
                if foodshop<1:
                    await main.send_message(chid, '<i>В клане нет фермы</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Продавать постройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE clandata SET farm=? WHERE group_id=?', (0, chid))
                conn.commit()
                cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance+500, a))
                conn.commit()
                await clancall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'sell_mailoffice':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT lootbox FROM clandata WHERE group_id = ?', (chid,))
                lootbox = cursor.fetchone()[0]
                if lootbox<1:
                    await main.send_message(chid, '<i>В клане нет почтового отделения</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Продавать постройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE clandata SET lootbox=? WHERE group_id=?', (0, chid))
                conn.commit()
                cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance+700, a))
                conn.commit()
                await clancall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'sell_chemists':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT apteka FROM clandata WHERE group_id = ?', (chid,))
                apteka = cursor.fetchone()[0]
                if apteka<1:
                    await main.send_message(chid, '<i>В клане нет аптеки</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Продавать постройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE clandata SET apteka=? WHERE group_id=?', (0, chid))
                conn.commit()
                cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance+500, a))
                conn.commit()
                await clancall(call)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'buy_canteen':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT foodshop FROM clandata WHERE group_id = ?', (chid,))
                foodshop = cursor.fetchone()[0]
                if foodshop>=1:
                    await main.send_message(chid, '<i>В клане уже есть столовая</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Покупать постройки для клана может только администратор чата</i>', parse_mode = 'html')
                    return
                if balance>=500:
                    cursor.execute('UPDATE clandata SET foodshop=? WHERE group_id=?', (foodshop+1, chid))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance-500, a))
                    conn.commit()
                    await clancall(call)
                else:
                    await call.answer('❌ У вас недостаточно средств', show_alert = True)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'buy_farm':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT farm FROM clandata WHERE group_id = ?', (chid,))
                farm = cursor.fetchone()[0]
                if farm>=1:
                    await main.send_message(chid, '<i>В клане уже есть ферма</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Покупать постройки для клана может только администратор чата</i>', parse_mode = 'html')
                    return
                if balance>=500:
                    cursor.execute('UPDATE clandata SET farm=? WHERE group_id=?', (farm+1, chid))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance-500, a))
                    conn.commit()
                    await clancall(call)
                else:
                    await call.answer('❌ У вас недостаточно средств', show_alert = True)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'buy_chemists':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT apteka FROM clandata WHERE group_id = ?', (chid,))
                apt = cursor.fetchone()[0]
                if apt>=1:
                    await main.send_message(chid, '<i>В клане уже есть аптека</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (a,))
                balance = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Покупать постройки для клана может только администратор чата</i>', parse_mode = 'html')
                    return
                if balance>=500:
                    cursor.execute('UPDATE clandata SET apteka=? WHERE group_id=?', (apt+1, chid))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET balance=? WHERE user_id=?', (balance-500, a))
                    conn.commit()
                    await clancall(call)
                else:
                    await call.answer('❌ У вас недостаточно средств', show_alert = True)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'donate_cow':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                cursor.execute('SELECT cow FROM userdata WHERE user_id=?', (a,))
                cow = cursor.fetchone()[0]
                if cow<1:
                    await call.answer(text='❌ У вас нет ни одной коровы', show_alert = True)
                    return
                cursor.execute('UPDATE userdata SET cow=cow-1 WHERE user_id=?', (a,))
                conn.commit()
                cursor.execute('UPDATE clandata SET cow=cow+1 WHERE group_id=?', (chid,))
                conn.commit()
                cursor.execute('SELECT cow FROM userdata WHERE user_id=?', (a,))
                cow = cursor.fetchone()[0]
                cursor.execute('SELECT cow FROM clandata WHERE group_id=?', (chid,))
                clancow = cursor.fetchone()[0]
                await call.answer(text='Передача совершена успешно. Теперь у вас {0} коров.\nВ клане теперь {1} коров'.format(cow, clancow), show_alert = True)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'milk_clan':
            try:
                a = call.from_user.id
                cursor.execute('SELECT nick FROM userdata WHERE user_id=?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id=?', (a,))
                rasa = cursor.fetchone()[0]
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                cursor.execute('SELECT cow FROM clandata WHERE group_id=?', (chid,))
                cow = cursor.fetchone()[0]
                if cow<1:
                    await call.answer(text='❌ В клане нет ни одной коровы', show_alert = True)
                    return
                cursor.execute('SELECT lastfarm FROM userdata WHERE user_id=?', (a,))
                lastfarm = cursor.fetchone()[0]
                diff = current_time()-lastfarm
                if diff>=86400:
                    cursor.execute('UPDATE clandata SET cow=cow-1 WHERE group_id=?', (chid,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET milk=milk+1 WHERE user_id=?', (a,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET lastfarm=? WHERE user_id=?', (current_time(), a,))
                    conn.commit()
                    cursor.execute('SELECT milk FROM userdata WHERE user_id=?', (a,))
                    milk = cursor.fetchone()[0]
                    await call.answer(text='Дойка прошла успешно. Теперь у вас {0} стаканов молока'.format(milk), show_alert = True)
                    await call.message.answer('<i><b><a href="tg://user?id={0}">{1}{2}</a></b> подоил корову</i>'.format(a, rasa, nick), parse_mode='html')
                else:
                    h = int(24-ceil(diff/3600))
                    m = int(60-ceil(diff%3600/60))
                    s = int(60-ceil(diff%3600%60))
                    await call.answer(text='Доить корову в клане можно раз в день. До следующей дойки осталось {0} часов {1} минут {2} секунд'.format(h, m, s), show_alert = True)
                    return
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'canteen':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT foodshop FROM clandata WHERE group_id = ?', (chid,))
                foodshop = cursor.fetchone()[0]
                if count == 0:
                    return
                markup = types.InlineKeyboardMarkup()
                lvl = ''
                if foodshop >=1:
                    markup.add(buybutton('porridge', 'clan'))
                    markup.add(buybutton('kisel', 'clan'))
                    markup.add(types.InlineKeyboardButton(text='💸 Продать постройку (возврат $500)', callback_data='sell_canteen'))
                else:
                    markup.add(types.InlineKeyboardButton(text='🍵 Купить - $500', callback_data='buy_canteen'))
                    lvl = '. В клане нет столовой'
                await main.send_message(chid, '<i>&#127861; <b>Столовая</b> - хорошее место для быстрого перекуса{0}</i>'.format(lvl), parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'chemists':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                cursor.execute('SELECT apteka FROM clandata WHERE group_id = ?', (chid,))
                apteka = cursor.fetchone()[0]
                if count == 0:
                    return
                markup = types.InlineKeyboardMarkup()
                lvl = ''
                if apteka >=1:
                    markup.add(buybutton('medicine', 'clan'))
                    markup.add(types.InlineKeyboardButton(text='💸 Продать постройку (возврат $500)', callback_data='sell_chemists'))
                else:
                    markup.add(types.InlineKeyboardButton(text='💊 Купить - $500', callback_data='buy_chemists'))
                    lvl = '. В клане нет столовой'
                await main.send_message(chid, '<i>&#128138; <b>Аптека</b> - тут можно купить лекарства дешевле, чем в Райбольнице{0}</i>'.format(lvl), parse_mode = 'html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clan_name':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Изменять настройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('clanname', a,))
                conn.commit()
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_process'))
                await main.send_message(chid, '<i>Введите новое название клана</i>', parse_mode = 'html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clan_photo':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Изменять настройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('clanphoto', a,))
                conn.commit()
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_process'))
                markup.add(types.InlineKeyboardButton(text='🗑 Удалить', callback_data='clear_clan_photo'))
                await main.send_message(chid, '<i>Отправьте ссылку на фото или само фото</i>', parse_mode='html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clear_clan_photo':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Изменять настройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
                cursor.execute('UPDATE clandata SET photo="" WHERE group_id=?', (chid,))
                conn.commit()
                await main.send_message(chid, '<i>Фото удалено</i>', parse_mode='html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clan_bio':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Изменять настройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('clanbio', a,))
                conn.commit()
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel_process'))
                markup.add(types.InlineKeyboardButton(text='🗑 Удалить', callback_data='clear_clan_bio'))
                await main.send_message(chid, '<i>Отправьте новое описание</i>', parse_mode='html', reply_markup = markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clear_clan_bio':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Изменять настройки клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE userdata SET process=? WHERE user_id=?', ('nothing', a,))
                conn.commit()
                cursor.execute('UPDATE clandata SET bio="" WHERE group_id=?', (chid,))
                conn.commit()
                await main.send_message(chid, '<i>Описание удалено</i>', parse_mode='html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'clear_headquarters':
            try:
                a = call.from_user.id
                chid = call.message.chat.id
                cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
                count = cursor.fetchone()[0]
                if count == 0:
                    return
                if not isinstance(await main.get_chat_member(chid, a), types.ChatMemberAdministrator) and not isinstance(await main.get_chat_member(chid, a), types.ChatMemberOwner):
                    await main.send_message(chid, '&#10060; <i>Снести штаб-квартиру клана может только администратор чата</i>', parse_mode = 'html')
                    return
                cursor.execute('UPDATE clandata SET hqplace=? WHERE group_id=?', ('', chid,))
                conn.commit()
                cursor.execute('UPDATE clandata SET address=0 WHERE group_id=?', (chid,))
                conn.commit()
                await main.send_message(chid, '<i>&#127970; Готово! Теперь штаб-квартира клана снесена</i>', parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'sign_up':
            await create_acc(call.from_user, call.message.chat.id)
        if call.data == 'clan_qrcode':
            try:
                chid = call.message.chat.id
                cursor.execute('SELECT username FROM clandata WHERE group_id=?', (chid,))
                username = cursor.fetchone()[0]
                cursor.execute('SELECT type FROM clandata WHERE group_id=?', (chid,))
                typ = cursor.fetchone()[0]
                if username=='':
                    await main.send_message(chid, '<i>У вашего клана нет ссылки, поэтому создать QR-код не получится</i>', parse_mode='html')
                    return
                if typ=='private':
                    await main.send_message(chid, '<i>Ваш клан частный, поэтому создать QR-код не получится</i>', parse_mode='html')
                    return
                color = '0-0-0'
                bgcolor = '255-255-255'
                style = random.choice(['', 'bgbluelight', 'bggreen', 'bgblack', 'red', 'blue', 'green',])
                if style=='bgbluelight':
                    color = '255-255-255'
                    bgcolor = '0-0-255'
                if style=='bgblue':
                    color = '0-0-0'
                    bgcolor = '0-0-255'
                if style=='bgred':
                    color = '0-0-0'
                    bgcolor = '255-0-0'
                if style=='bggreen':
                    color = '0-0-0'
                    bgcolor='0-255-0'
                if style=='bgyellow':
                    color = '0-0-0'
                    bgcolor = '255-255-0'
                if style=='bgblack':
                    color = '255-255-255'
                    bgcolor = '0-0-0'
                if style=='bgpink':
                    color = '0-0-0'
                    bgcolor = '255-0-255'
                if style=='bgcyan':
                    color = '0-0-0'
                    bgcolor = '0-255-255'
                if style=='red':
                    color = '255-0-0'
                    bgcolor = '255-255-255'
                if style=='blue':
                    color = '0-0-255'
                    bgcolor = '255-255-255'
                if style=='green':
                    color = '0-255-0'
                    bgcolor = '255-255-255'
                if style=='cyan':
                    color = '0-255-255'
                    bgcolor = '255-255-255'
                if style=='pink':
                    color = '255-0-255'
                    bgcolor = '255-255-255'
                if style=='yellow':
                    color = '255-255-0'
                    bgcolor = '0-0-0'
                if style=='yellowlight':
                    color = '255-255-0'
                    bgcolor = '255-255-255'
                await main.send_photo(call.message.chat.id, 'https://api.qrserver.com/v1/create-qr-code/?data={0}&size=512x512&charset-source=UTF-8&charset-target=UTF-8&ecc=L&color={1}&bgcolor={2}&margin=1&qzone=1&format=png'.format(username, color, bgcolor), '<i>QR-код готов</i>', parse_mode = 'html')
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data == 'local_clans':
            try:
                a = call.from_user.id
                cursor.execute('SELECT place FROM userdata WHERE user_id = ?', (a,))
                place = cursor.fetchone()[0]
                clans = ''
                cursor.execute('SELECT count(*) FROM clandata WHERE hqplace = ? AND type=?', (place, 'public',))
                count = cursor.fetchone()[0]
                if count == 0:
                    await call.message.answer('<i>В этой местности кланов нет :(</i>', parse_mode = 'html')
                    return
                cursor.execute('SELECT * FROM clandata WHERE hqplace = ? AND type = ? ORDER BY address LIMIT 50', (place, 'public',))
                for row in cursor:
                    clans+='\n<b>{0}.</b> <a href = "{1}">{2}</a>'.format(row[11], row[8], row[1])
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text='Искать по номеру дома', callback_data='hq_number'))
                await call.message.answer('<i>&#127970; Кланы поблизости: <b>{0}</b></i>'.format(clans), parse_mode = 'html', reply_markup=markup)
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
        if call.data.startswith('battle_'):
            try:
                await battle(call.message, call.from_user.id, int(call.data[7:]))
            except Exception as e:
                await call.message.answer('&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
                await call.message.answer('<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')
    
    @bot.message_handler(content_types=['new_chat_members'])
    async def welcome_new_member(message: types.Message):
        if message.new_chat_members[0].id == ID:
            await main.send_photo(message.chat.id, 'https://te.legra.ph/file/c1ee7f35883ab50abcde5.jpg', caption='''<i><b>🥳 Мы дождались этого момента!</b>
😼 Пока Бойцовский клуб потихоньку умирал, в тайне (ну, как сказать в тайне, про это знали многие игроки БК :) велась разработка новой игры — Живополиса
🚆 Акцент в этой игре делается не на жестокие битвы, а на мирные путешествия (хотя жестокие битвы на бан тоже можно проводить :)
💼 Работай, зарабатывай деньги и трать их в многочисленных магазинах по всему Живополису (а ещё деньги можно красть, но лучше так не делать, ибо админы всё видят👀 :)
👦🏿 Ты можешь стать кем угодно, от енота до нигера (нет, последним нельзя или бан :)
🤬 У нас всё под контролем. За нарушение правил добрые админы вам обнулят аккаунт</i>''', parse_mode = 'html')
        else:
            await startdef(message)
    
    @inline.bot
            if money<0 and whole:
                markup.add(types.InlineKeyboardButton(text='💵 Оплатить счёт', callback_data='paybill {0} {1}'.format(-money, a)))
                item.append(InlineQueryResultArticle(
                    id = 'bill_{0}'.format(money),
                    title = f'💵 Отправить счёт на сумму ${-money}',
                    description='Баланс: ${0}'.format(balance),
                    input_message_content=InputTextMessageContent('<i>&#128181; <b><a href="tg://user?id={3}">{0}{1}</a></b> выставил вам счёт на сумму <b>${2}</b></i>'.format(rasa, nick, -money, a), parse_mode='html'),
                    reply_markup = markup,
                ))
            if not whole:
                item.append(InlineQueryResultArticle(
                    id = 'error',
                    title = f'💲 Отправить чек на сумму $',
                    description='❌ Введите целое число после знака $\nБаланс: ${0}'.format(balance),
                    input_message_content=InputTextMessageContent('<i>Нужно ввести целое число</i>', parse_mode='html'),
                    reply_markup = markup,
                ))
            if item[0].id.startswith('check_'):
                money = int(item[0].id[6:])
                if money>balance:
                    return
                else:
                    cursor.execute('UPDATE userdata SET balance=balance-? WHERE user_id=?', (money, a,))
                    conn.commit()
        elif text.startswith('%'):
            try:
                money = int(text[1:])
            except:
                money = 0
                whole = False
            markup = types.InlineKeyboardMarkup()
            if money>=0 and whole:
                for itid in ITEMS[1]:
                    markup = types.InlineKeyboardMarkup()
                    if money == 0:
                        markup.add(types.InlineKeyboardButton(text='Забрать бесплатно', callback_data='slot {0} 0 {1}'.format(itid, a)))
                    else:
                        markup.add(types.InlineKeyboardButton(text='Купить за ${0}'.format(money), callback_data='slot {0} {1} {2}'.format(itid, money, a)))
                    ids = ITEMS[1].index(itid)
                    if itemdata(a, itid)!='emptyslot':
                        cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(itid), (a,))
                        amt = cursor.fetchone()[0]
                        item.append(InlineQueryResultArticle(
                            id = 'slot {0} {1}'.format(ids, money),
                            title = 'Продать {0}{1} за ${2}'.format(ITEMS[0][ids], ITEMS[2][ids], money),
                            description = 'У вас этого предмета: {0}'.format(amt),
                            input_message_content=InputTextMessageContent('<i><b><a href="tg://user?id={3}">{0}{1}</a></b> предлагает вам <b>{4} {5}</b> за <b>${2}</b></i>'.format(rasa, nick, money, a, ITEMS[0][ids], ITEMS[2][ids]), parse_mode='html'),
                            reply_markup = markup,
                        ))
            if not whole or money<0:
                item.append(InlineQueryResultArticle(
                    id = 'error',
                    title = f'🚫 Продать товар за $',
                    description='❌ Введите целое неотрицательное число после знака $'.format(balance),
                    input_message_content=InputTextMessageContent('<i>Нужно ввести целое неотрицательное число</i>', parse_mode='html'),
                    reply_markup = markup,
                ))
            for inst in item:
                if inst.id.startswith('slot '):
                    itid = ITEMS[1][int(inst.id.split(' ')[1])]
                    cursor.execute('SELECT {0} FROM userdata WHERE user_id=?'.format(itid), (a,))
                    amt = cursor.fetchone()[0]
                    if amt<1:
                        return
                    else:
                        cursor.execute('UPDATE userdata SET {0}={0}-1 WHERE user_id=?'.format(itid), (a,))
                        conn.commit()
        else:
            item.append(InlineQueryResultArticle(
                id = 'help',
                title = 'Команды',
                description = '${сумма} - выписать чек или счёт\n%{стоимость} - продать товар\nНажмите для подробностей',
                input_message_content=InputTextMessageContent('<i><b>Команды</b>\n<code>${сумма}</code> - выписать чек (или счёт, если сумма отрицательная) на указанную сумму.\n<code>%{цена}</code> - продать выбранный товар по указанной цене</i>', parse_mode='html'),
            ))

    @bot.chosen_inline_handler()
    async def huy():
        if query.startswith('%'):
                        cost = int(query[1:])
                        if cost>0:
                            itid = int(i.result_id.split(' ')[1])
                            itm = ITEMS[0][itid]+' '+ITEMS[2][itid]
                            await main.send_message(fid, '<i><b><a href="tg://user?id={3}">{0}{1}</a></b> продаёт <b>{4}</b> за <b>${2}</b>\n#user_sellitem</i>'.format(rasa, nick, cost, a, itm), parse_mode='html')
                except Exception as e:
                    print(e)