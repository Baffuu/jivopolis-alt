import contextlib
from ..database import cur
from ..database.functions import check, current_time
from ..misc import get_embedded_link, get_link, get_mask
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChosenInlineResult
)
from .. import logger, bot, Dispatcher, tglog
from ..misc import OfficialChats


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

        in_prison: int = cur.select("prison_started", "userdata").where(
            user_id=user_id).one() - current_time()
        if in_prison > 0:
            return await bot.answer_inline_query(
                query.id,
                [
                    InlineQueryResultArticle(
                        id = 'prison',  # noqa: E251
                        title = '👮‍♂️ Вы находитесь в тюрьме',  # noqa: E251, E501
                        description = 'Подождите, пока срок закончится',  # noqa: E251, E501
                        input_message_content =   # noqa: E251
                        InputTextMessageContent(
                            "<i>👮‍♂️ Вы находитесь в тюрьме. Подождите, пока "
                            "ваш срок закончится</i>"
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

        match(data):
            case None:
                pass
            case give if give.startswith('$'):
                results = await givemoney_query(
                    data, balance, results,
                    user_id, mask, nick  # type: ignore
                )
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


def register(dp: Dispatcher):
    dp.register_inline_handler(inline_mode)
    dp.register_chosen_inline_handler(on_pressed_inline_query)
