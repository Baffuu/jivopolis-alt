import contextlib

from ..database import cur
from ..database.functions import check, itemdata
from ..misc import get_embedded_link, get_link, get_mask
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChosenInlineResult,
)
from .. import logger, bot, Dispatcher, tglog
from ..marketplace.marketplace import market
from ..misc import OfficialChats
from ..items import ITEMS


def str_to_bool(__s: str):
    return __s == "True"


async def inline_mode(query: InlineQuery):
    try:
        user_id = query.from_user.id
        await check(user_id, user_id)
        results = []
        try:
            health: int = cur.select("health", "userdata").where(
                user_id=query.from_user.id).one()
            is_banned = bool(cur.select("is_banned", "userdata").where(
                user_id=query.from_user.id).one())
            assert health is not None
        except AssertionError:
            return

        if is_banned:
            return await bot.answer_inline_query(
                query.id,
                [
                    InlineQueryResultArticle(
                        id = 'banned',  # noqa: E251
                        title = '🧛🏻‍♂️ Вы были забанены в боте.',  # noqa: E251, E501
                        description = 'Если вы считаете, что это ошибка, обратитесь в поддержку',  # noqa: E251, E501
                        input_message_content =   # noqa: E251
                        InputTextMessageContent(
                            "<i>🧛🏻‍♂️ Вы были забанены в боте. Если вы считает"
                            "е, что это ошибка, обратитесь в <a href = "
                            f"'{OfficialChats.SUPPORTCHATLINK}'>"
                            "поддержку</a></i>"
                        )
                    )
                ]
            )

        if health < 0:
            return await bot.answer_inline_query(
                query.id,
                [
                    InlineQueryResultArticle(
                        id = 'dead',  # noqa: E251
                        title = '☠️ Вы умерли',  # noqa: E251
                        description = 'Попросите кого-нибудь вас воскресить',  # noqa: E251, E501
                        input_message_content = InputTextMessageContent(  # noqa: E251, E501
                            '<i>☠️ Вы умерли. Попросите кого-нибудь вас воскресить</i>'  # noqa: E501
                            )
                    )
                ]
            )

        data = query.query

        try:
            nick = cur.select("nickname", "userdata").where(
                user_id=user_id).one()
            mask = get_mask(user_id)
            balance = cur.select("balance", "userdata").where(
                user_id=user_id).one()
            assert nick is not None
        except AssertionError:
            results.append(
                InlineQueryResultArticle(
                    id='account_not_found',
                    title='👤 Аккаунт не найден',
                    description='Попробуйте зайти в бота и создать новый!',
                    input_message_content=InputTextMessageContent(
                        '<i>🐸 Ваш аккаунт не найден. Нажмите на кнопку ниже '
                        'чтобы его создать</i>'
                    ),
                    reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton(
                                "Создать аккаунт",
                                callback_data="sign_up"
                            )
                        )
                    )
                )
            mask = None
            nick = None
            balance = 0
            data = None

        match (data):
            case None:
                pass
            case give if give.startswith('$'):
                results = await givemoney_query(
                    data, balance, results,
                    user_id, mask, nick  # type: ignore
                )
            case sell if sell.startswith("%"):
                results = await sell_query(data, user_id)

        return await bot.answer_inline_query(query.id, results, 1)
    except Exception as e:
        logger.exception(e)


async def on_pressed_inline_query(inline: ChosenInlineResult):
    with contextlib.suppress(Exception):
        user_id = inline.from_user.id
        # nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id={user_id}").fetchone()[0] # noqa
        data = inline.query
        if data.startswith('$'):
            money = int(data[1:])
            if money > 0:
                cur.update("userdata").add(balance=-money).where(
                    user_id=user_id).commit()
                await tglog(
                    f'<i>💲 <b>{await get_embedded_link(user_id)}</b> '
                    f'выписал чек на <b>${money}</b>', '#user_check</i>'
                )
            if money < 0:
                await tglog(
                    f'<i>💲 <b>{await get_embedded_link(user_id)}</b> '
                    f'выставил счёт на <b>${money}</b>', '#user_bill</i>'
                )
        elif data.startswith("%"):
            cost = int(data[1:])
            item = ITEMS[inline.result_id.split(" ")[1]]
            cur.update("userdata").add(**{item.name: -1}).where(
                user_id=inline.from_user.id).commit()
            if cost > 0:  # if item is not free

                if str_to_bool(inline.result_id.split(" ")[4]):
                    market.publish(
                        user_id,
                        item,
                        cost,
                        inline.result_id.split(" ")[5]
                    )

                await tglog(
                    f"{await get_embedded_link(user_id)} продаёт {item.emoji}"
                    f"{item.ru_name} за ${cost}",
                    "#user_sellitem"
                )


async def givemoney_query(
    data: str,
    balance: int,
    results: list,
    user_id: int,
    mask: str,
    nick: str
):
    try:
        money = int(data[1:])
    except Exception:
        money = 0

    markup = InlineKeyboardMarkup()

    try:
        if money > 0:
            if balance >= money:
                markup.add(
                    InlineKeyboardButton(
                        text='💲 Забрать деньги',
                        callback_data=f'check_{money}'
                    )
                )

                results.append(
                    InlineQueryResultArticle(
                        id=f'check_{money}',
                        title=f'💲 Отправить чек на сумму ${money}',
                        description=f'Баланс: ${balance}',
                        input_message_content=InputTextMessageContent(
                            f'<i>💲 <b><a href="tg://user?id={user_id}"'
                            f'>{mask}{nick}</a></b> предлагает вам <b>${money}'
                            '</b></i>'
                        ),
                        reply_markup=markup,
                    )
                )
            else:
                markup.add(
                    InlineKeyboardButton(
                        text='💲 Забрать деньги',
                        callback_data=f'check_{balance}'
                    )
                )

                results.append(InlineQueryResultArticle(
                    id=f'check_{balance}',
                    title=f'💲 Отправить чек на сумму ${balance}',
                    description=f'Баланс: ${balance}',
                    input_message_content=InputTextMessageContent(
                        f'<i>💲 <b><a href="{await get_link(user_id)}"'
                        f'>{mask}{nick}</a></b> предлагает вам <b>${balance}<'
                        '/b></i>'
                    ),
                    reply_markup=markup,
                ))
    except TypeError:
        results.append(InlineQueryResultArticle(
            id='check_error',
            title='🚫 Введите правильное число',
            description=(
                'Это должно быть целое число, не текст и не десятичная дробь'
            ),
            input_message_content=InputTextMessageContent(
                '🚫 Введите правильное число'),
        ))

    return results


async def sell_query(
    text: str,
    user_id: int
):
    post_on_market = "-b" not in text  # todo: make constant for "-b"
    if not post_on_market:
        text = text.replace("-b", "")
    try:
        money = int(text[1:])
    except Exception:
        money = -1

    markup = InlineKeyboardMarkup()
    index = 0
    results: list[InlineQueryResultArticle] = []

    def get_query(itemname: str):
        return f'slot {itemname} {money} {user_id} {post_on_market} {market.generate_temp()}'  # noqa: E501

    for itemname in ITEMS:
        if index > 15:  # to show only first 15 results
            # todo: make constant
            break

        itemdata_ = await itemdata(user_id, itemname)

        if itemdata_ == "emptyslot" or itemdata_ is None:
            continue
        data = get_query(itemname)
        if money == 0:
            markup.inline_keyboard
            markup.inline_keyboard = [
                [
                    InlineKeyboardButton(
                        text='Забрать бесплатно',
                        callback_data=data
                    )
                ]
            ]
        elif money > 0:
            markup.inline_keyboard = [
                [
                    InlineKeyboardButton(
                        text=f'Купить за ${money}',
                        callback_data=data
                    )
                ]
            ]

        amount = cur.select(itemname, "userdata").where(
            user_id=user_id).one()
        item = ITEMS[itemname]
        results.append(
            InlineQueryResultArticle(
                id=data,
                title=f'Продать {item.emoji}{item.ru_name} за ${money}',
                description=f'У вас этого предмета: {amount}',
                input_message_content=InputTextMessageContent(
                    f'<i>{await get_embedded_link(user_id)} предлагает вам'
                    f' <b>{item.emoji} {item.ru_name}</b> за <b>${money}</'
                    'b></i>'
                ),
                reply_markup=markup,
            )
        )
        index += 1

    if money < 0:
        results.append(
            InlineQueryResultArticle(
                id='error',
                title='🚫 Продать товар за $X',
                description='❌ Введите целое неотрицательное число после'
                            f' знака ${money}',
                input_message_content=InputTextMessageContent(
                    '<i>Нужно ввести целое неотрицательное число</i>'
                ),
                reply_markup=markup,
            )
        )
    return results


def register(dp: Dispatcher):
    dp.register_inline_handler(inline_mode)
    dp.register_chosen_inline_handler(on_pressed_inline_query)
