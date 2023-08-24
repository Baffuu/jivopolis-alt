import contextlib
from fyCursor import connect, fyCursor, Table, Field, DATATYPES
import sqlite3

from typing import Tuple, Optional, NoReturn, Any

from ..bot import bot
from loguru import logger

from aiogram.types import User, Chat
from aiogram.utils.deep_linking import encode_payload


def connect_database() -> Tuple[
    sqlite3.Connection,
    fyCursor,
    dict[str, Table]
] | NoReturn:
    """
    connects database, creates tables if they do not exists, etc.
    """
    cur = connect('database.db')
    if conn := cur.connection:
        tables = _connect_tables(cur)
        return conn, cur, tables
    logger.critical('database is not connected')
    raise RuntimeError('database is not connected')


def _connect_tables(cur: fyCursor) -> dict[str, Table]:
    create_userdata(cur)
    create_globaldata(cur)
    create_clandata(cur)
    create_cryptodata(cur)
    marketplace = create_marketplace(cur)
    logger.success('Database connected')
    return {
        "marketplace": marketplace
    }


def create_userdata(cur: fyCursor) -> None:
    '''
    creates table with all users data
    '''
    cur.execute(""" CREATE TABLE IF NOT EXISTS userdata
(
    id              INTEGER         PRIMARY KEY,
    user_id         INTEGER                                 NOT NULL,
    nickname        TEXT,
    description     TEXT            DEFAULT \"пусто\"       NOT NULL,
    balance         INTEGER         DEFAULT 0               NOT NULL,
    profile_type    TEXT            DEFAULT \"public\"      NOT NULL,
    photo_id        TEXT,
    rase            VARCHAR         DEFAULT \"🤔\"          NOT NULL,
    mask            TEXT,
    inviter_id      INTEGER         DEFAULT 0               NOT NULL,

    login_id        TEXT,
    login_password  TEXT            DEFAULT 0               NOT NULL,

    health          INTEGER         DEFAULT 100             NOT NULL,
    level           INTEGER         DEFAULT 0               NOT NULL,
    XP              INTEGER         DEFAULT 0               NOT NULL,
    clan_id         INTEGER,
    last_steal      DATETIME        DEFAULT 0               NOT NULL,
    is_ready        INTEGER         DEFAULT 0               NOT NULL,

    nonick_cmds     INTEGER         DEFAULT 0               NOT NULL,
    last_box        DATETIME        DEFAULT 0               NOT NULL,
    total_jackpots  INTEGER         DEFAULT 0               NOT NULL,
    last_gameclub   INTEGER         DEFAULT 0               NOT NULL,

    current_place   TEXT            DEFAULT \"Вокзальная\"  NOT NULL,
    line            INTEGER         DEFAULT 2               NOT NULL,
    left_transport  INTEGER         DEFAULT 0               NOT NULL,

    sql             TEXT,
    rank            INTEGER         DEFAULT 0               NOT NULL,
    process         TEXT,
    is_banned       BOOL            DEFAULT False           NOT NULL,
    lastseen        DATETIME        DEFAULT 0               NOT NULL,
    register_date   DATETIME        DEFAULT 0               NOT NULL,
    last_fight      DATETIME        DEFAULT 0               NOT NULL,
    prison_started  DATETIME        DEFAULT 0               NOT NULL,
    last_geography  DATETIME        DEFAULT 0               NOT NULL,
    last_math       DATETIME        DEFAULT 0               NOT NULL,
    last_gears      DATETIME        DEFAULT 0               NOT NULL,
    gears_today     INTEGER         DEFAULT 0               NOT NULL,
    task_message    INTEGER         DEFAULT 0               NOT NULL,
    last_milk       DATETIME        DEFAULT 0               NOT NULL,
    last_fish       DATETIME        DEFAULT 0               NOT NULL,
    last_mine       DATETIME        DEFAULT 0               NOT NULL,
    last_proc       DATETIME        DEFAULT 0               NOT NULL,
    fish_message    INTEGER         DEFAULT 0               NOT NULL,

    fyCoin          INTEGER         DEFAULT 0               NOT NULL,
    Mithereum       INTEGER         DEFAULT 0               NOT NULL,
    Gather          INTEGER         DEFAULT 0               NOT NULL,
    Recegon         INTEGER         DEFAULT 0               NOT NULL,

    walrus          INTEGER         DEFAULT 0               NOT NULL,
    lootbox         INTEGER         DEFAULT 0               NOT NULL,
    cow             INTEGER         DEFAULT 0               NOT NULL,
    key             INTEGER         DEFAULT 0               NOT NULL,
    fox             INTEGER         DEFAULT 0               NOT NULL,
    gun             INTEGER         DEFAULT 0               NOT NULL,
    wolf            INTEGER         DEFAULT 0               NOT NULL,
    parrot          INTEGER         DEFAULT 0               NOT NULL,
    vest            INTEGER         DEFAULT 0               NOT NULL,
    japanese_goblin INTEGER         DEFAULT 0               NOT NULL,
    ninja           INTEGER         DEFAULT 0               NOT NULL,
    bomb            INTEGER         DEFAULT 0               NOT NULL,
    confetti        INTEGER         DEFAULT 0               NOT NULL,
    fireworks       INTEGER         DEFAULT 0               NOT NULL,
    party_popper    INTEGER         DEFAULT 0               NOT NULL,
    mrs_claus       INTEGER         DEFAULT 0               NOT NULL,
    santa_claus     INTEGER         DEFAULT 0               NOT NULL,
    fairy qq        INTEGER         DEFAULT 0               NOT NULL,
    snowflake       INTEGER         DEFAULT 0               NOT NULL,
    snowman         INTEGER         DEFAULT 0               NOT NULL,
    hedgehog        INTEGER         DEFAULT 0               NOT NULL,
    truck           INTEGER         DEFAULT 0               NOT NULL,
    gold_medal      INTEGER         DEFAULT 0               NOT NULL,
    silver_medal    INTEGER         DEFAULT 0               NOT NULL,
    bronze_medal    INTEGER         DEFAULT 0               NOT NULL,
    poison          INTEGER         DEFAULT 0               NOT NULL,
    pill            INTEGER         DEFAULT 0               NOT NULL,
    baguette        INTEGER         DEFAULT 0               NOT NULL,
    milk            INTEGER         DEFAULT 0               NOT NULL,
    ramen           INTEGER         DEFAULT 0               NOT NULL,
    pelmeni         INTEGER         DEFAULT 0               NOT NULL,
    apple           INTEGER         DEFAULT 0               NOT NULL,
    shawarma        INTEGER         DEFAULT 0               NOT NULL,
    burger          INTEGER         DEFAULT 0               NOT NULL,
    pizza           INTEGER         DEFAULT 0               NOT NULL,
    coconut         INTEGER         DEFAULT 0               NOT NULL,
    kiwi            INTEGER         DEFAULT 0               NOT NULL,
    tomato          INTEGER         DEFAULT 0               NOT NULL,
    fries           INTEGER         DEFAULT 0               NOT NULL,
    cucumber        INTEGER         DEFAULT 0               NOT NULL,
    spaghetti       INTEGER         DEFAULT 0               NOT NULL,
    doughnut        INTEGER         DEFAULT 0               NOT NULL,
    bento           INTEGER         DEFAULT 0               NOT NULL,
    beer            INTEGER         DEFAULT 0               NOT NULL,
    meat_on_bone    INTEGER         DEFAULT 0               NOT NULL,
    cheburek        INTEGER         DEFAULT 0               NOT NULL,
    tea             INTEGER         DEFAULT 0               NOT NULL,
    coffee          INTEGER         DEFAULT 0               NOT NULL,
    rice            INTEGER         DEFAULT 0               NOT NULL,
    cookie          INTEGER         DEFAULT 0               NOT NULL,
    cake            INTEGER         DEFAULT 0               NOT NULL,
    sake            INTEGER         DEFAULT 0               NOT NULL,
    pita            INTEGER         DEFAULT 0               NOT NULL,
    red_car         INTEGER         DEFAULT 0               NOT NULL,
    blue_car        INTEGER         DEFAULT 0               NOT NULL,
    racing_car      INTEGER         DEFAULT 0               NOT NULL,
    clown           INTEGER         DEFAULT 0               NOT NULL,
    ghost           INTEGER         DEFAULT 0               NOT NULL,
    alien           INTEGER         DEFAULT 0               NOT NULL,
    robot           INTEGER         DEFAULT 0               NOT NULL,
    shit            INTEGER         DEFAULT 0               NOT NULL,
    fondue          INTEGER         DEFAULT 0               NOT NULL,
    juice           INTEGER         DEFAULT 0               NOT NULL,
    cactus          INTEGER         DEFAULT 0               NOT NULL,
    palm            INTEGER         DEFAULT 0               NOT NULL,
    potted_plant    INTEGER         DEFAULT 0               NOT NULL,
    clover          INTEGER         DEFAULT 0               NOT NULL,
    tulip           INTEGER         DEFAULT 0               NOT NULL,
    rose            INTEGER         DEFAULT 0               NOT NULL,
    xmas_tree       INTEGER         DEFAULT 0               NOT NULL,
    moyai           INTEGER         DEFAULT 0               NOT NULL,
    chocolate       INTEGER         DEFAULT 0               NOT NULL,
    shaved_ice      INTEGER         DEFAULT 0               NOT NULL,
    ice_cream       INTEGER         DEFAULT 0               NOT NULL,
    stethoscope     INTEGER         DEFAULT 0               NOT NULL,
    metrotoken      INTEGER         DEFAULT 0               NOT NULL,
    traintoken      INTEGER         DEFAULT 0               NOT NULL,
    phone           INTEGER         DEFAULT 0               NOT NULL,
    trolleytoken    INTEGER         DEFAULT 0               NOT NULL,
    tramtoken       INTEGER         DEFAULT 0               NOT NULL,
    regtraintoken   INTEGER         DEFAULT 0               NOT NULL,
    hamster         INTEGER         DEFAULT 0               NOT NULL,
    fan             INTEGER         DEFAULT 0               NOT NULL,
    pickaxe         INTEGER         DEFAULT 0               NOT NULL,
    fishing_rod     INTEGER         DEFAULT 0               NOT NULL,
    beaver          INTEGER         DEFAULT 0               NOT NULL,
    penguin         INTEGER         DEFAULT 0               NOT NULL,
    seashell        INTEGER         DEFAULT 0               NOT NULL,
    blue_fish       INTEGER         DEFAULT 0               NOT NULL,
    tropical_fish   INTEGER         DEFAULT 0               NOT NULL,
    blowfish        INTEGER         DEFAULT 0               NOT NULL,
    shrimp          INTEGER         DEFAULT 0               NOT NULL,
    fried_shrimp    INTEGER         DEFAULT 0               NOT NULL,

    cobble          INTEGER         DEFAULT 0               NOT NULL,
    coal            INTEGER         DEFAULT 0               NOT NULL,
    iron            INTEGER         DEFAULT 0               NOT NULL,
    gold            INTEGER         DEFAULT 0               NOT NULL,
    gem             INTEGER         DEFAULT 0               NOT NULL,
    topaz           INTEGER         DEFAULT 0               NOT NULL,

    cab_achieve     INTEGER         DEFAULT 0               NOT NULL,
    shuttle_achieve INTEGER         DEFAULT 0               NOT NULL,
    plane_achieve   INTEGER         DEFAULT 0               NOT NULL,
    walk_achieve    INTEGER         DEFAULT 0               NOT NULL,
    walk_progress   INTEGER         DEFAULT 0               NOT NULL,
    luck_achieve    INTEGER         DEFAULT 0               NOT NULL,
    jackpot_progress INTEGER        DEFAULT 0               NOT NULL,
    jackpot_achieve INTEGER         DEFAULT 0               NOT NULL,
    all_achieve     INTEGER         DEFAULT 0               NOT NULL,
    auto_achieve    INTEGER         DEFAULT 0               NOT NULL,
    mask_achieve    INTEGER         DEFAULT 0               NOT NULL,
    sell_progress   INTEGER         DEFAULT 0               NOT NULL,
    sell_achieve    INTEGER         DEFAULT 0               NOT NULL,
    tram_achieve    INTEGER         DEFAULT 0               NOT NULL,
    fish_achieve    INTEGER         DEFAULT 0               NOT NULL,
    fish_progress   INTEGER         DEFAULT 0               NOT NULL,
    proc_achieve    INTEGER         DEFAULT 0               NOT NULL
)
""")


def create_globaldata(cur: fyCursor) -> None:
    """
    creates global jivopolis data
    """
    cur.execute("""CREATE TABLE IF NOT EXISTS globaldata
(
    treasury        INTEGER         DEFAULT 0               NOT NULL,
    lastfill        DATETIME        DEFAULT 0               NOT NULL,
    lastcrypto      DATETIME        DEFAULT 0               NOT NULL,
    lastmarket      DATETIME        DEFAULT 0               NOT NULL,
    baguette        INTEGER,
    pelmeni         INTEGER,
    soup            INTEGER,
    meat_on_bone    INTEGER,
    pita            INTEGER,
    tea             INTEGER
)""")


def create_clandata(cur: fyCursor) -> None:
    cur.execute("""CREATE TABLE IF NOT EXISTS clandata
(
    id              INTEGER         PRIMARY KEY,
    clan_id         INTEGER,
    clan_name       TEXT,
    clan_type       TEXT            DEFAULT \"public\"      NOT NULL,
    clan_balance    INTEGER         DEFAULT 0               NOT NULL,
    owner_id        INTEGER,
    HQ_place        TEXT        DEFAULT \"не установлено\"  NOT NULL,
    address         INTEGER,
    link            TEXT,
    lootbox         INTEGER         DEFAULT 0               NOT NULL,
    last_box        DATETIME        DEFAULT 0               NOT NULL,
    description     TEXT,
    photo_id        TEXT,
    addon_location  INTEGER         DEFAULT 0               NOT NULL,
    addon_gameclub  INTEGER         DEFAULT 0               NOT NULL,
    filter_sticker  INTEGER         DEFAULT 0               NOT NULL,
    filter_photo    INTEGER         DEFAULT 0               NOT NULL,
    filter_dice     INTEGER         DEFAULT 0               NOT NULL,
    filter_voice    INTEGER         DEFAULT 0               NOT NULL,
    filter_video    INTEGER         DEFAULT 0               NOT NULL,
    filter_join     INTEGER         DEFAULT 0               NOT NULL,
    filter_leave    INTEGER         DEFAULT 0               NOT NULL,
    filter_document INTEGER         DEFAULT 0               NOT NULL,
    filter_location INTEGER         DEFAULT 0               NOT NULL,
    filter_contact  INTEGER         DEFAULT 0               NOT NULL,
    filter_gif      INTEGER         DEFAULT 0               NOT NULL,
    game_timeout    INTEGER         DEFAULT 10              NOT NULL,
    build_mail      INTEGER         DEFAULT 0               NOT NULL,
    build_canteen   INTEGER         DEFAULT 0               NOT NULL,
    build_pharmacy  INTEGER         DEFAULT 0               NOT NULL,
    build_farm      INTEGER         DEFAULT 0               NOT NULL,
    cows            INTEGER         DEFAULT 0               NOT NULL,
    last_lootbox    DATETIME        DEFAULT 0               NOT NULL,
    last_withdrawal DATETIME        DEFAULT 0               NOT NULL
)
    """)


def create_cryptodata(cur: fyCursor) -> None:
    with contextlib.suppress(sqlite3.OperationalError):
        cur.execute("""SELECT * FROM cryptodata""").fetchone()
        return

    cur.execute("""
    CREATE TABLE IF NOT EXISTS
    cryptodata(
        id INTEGER PRIMARY KEY,
        crypto TEXT NOT NULL,
        value INTEGER DEFAULT 5 NOT NULL,
        bought INTEGER DEFAULT 0 NOT NULL,
        sold INTEGER DEFAULT 0 NOT NULL,
        prev_value INTEGER,
        hours_8 INTEGER,
        hours_12 INTEGER,
        hours_16 INTEGER,
        hours_20 INTEGER,
        hours_24 INTEGER
    )
    """)
    from ..items import ITEMS

    for i in [item for item in ITEMS if ITEMS[item].type == "crypto"]:
        cur.execute(f"INSERT INTO cryptodata(crypto) VALUES (\"{i}\")")


def create_marketplace(cur: fyCursor) -> Table:
    fields = {
        "id": Field(primary_key=True, type=DATATYPES.INTEGER),
        "type": Field(nullable=False, type=DATATYPES.TEXT),
        "seller_id": Field(nullable=False, type=DATATYPES.INTEGER),
        "put_up_date": Field(type=DATATYPES.TIMESTAMP),
        "cost": Field(nullable=False, type=DATATYPES.INTEGER),
        "temp_id": Field(nullable=False, type=DATATYPES.INTEGER)
    }

    global market_table
    market_table = Table(name="marketplace", cursor=cur, kwargs_fields=fields)
    return market_table.create(True)


async def insert_clan(
    chat: Chat, user: Optional[User] | dict[Any, Any] = None
) -> str:
    '''
    inserts chat into clandata

    :param chat - chat that will be inserted
    :param user - (Optional) clan creator

    :returns - new chat invite link
    '''

    if user is None:
        user = {'id': None}

    link = await bot.create_chat_invite_link(
        chat.id, name='Jivopolis Default Invite Link'
    )

    from . import cur, conn
    cur.execute(
        f"INSERT INTO clandata(clan_id, clan_name, owner_id, link) VALUES"
        f"({chat.id}, '{chat.title}', '{user['id']}', '{link.invite_link}')"
    )
    conn.commit()
    return link.invite_link


def insert_user(user: User) -> None:
    """
    insets user into userdata table

    :param user (aiogram.types.User) - user that will be inserted
    """
    logger.info("user inserted")
    name = user.full_name  # type: ignore
    login_id = encode_payload(str(user.id))
    from . import cur, conn
    cur.execute(
        "INSERT INTO userdata(user_id, nickname, login_id) "
        f"VALUES ({user.id}, \"{name}\", \"{login_id}\")"
    )
    conn.commit()
