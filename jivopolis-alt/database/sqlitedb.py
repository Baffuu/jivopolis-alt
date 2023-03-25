import sqlite3

from aiogram.types import User, Chat, ChatInviteLink
from aiogram.utils.deep_linking import encode_payload
from .. import logger, bot 

def connect_database() -> None:
    global conn, cur
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cur = conn.cursor()
    if conn:
        create_userdata()
        create_globaldata()
        create_clandata()
        return logger.success('database connected')
    return logger.critical('database is not connected')

def create_userdata() -> None:
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
    clan_id         INTEGER         DEFAULT 0               NOT NULL,
    last_steal      DATETIME        DEFAULT 0               NOT NULL,
    is_ready        INTEGER         DEFAULT 0               NOT NULL,

    last_box        DATETIME        DEFAULT 0               NOT NULL,
    total_jackpots  INTEGER         DEFAULT 0               NOT NULL,

    current_place   TEXT            DEFAULT \"Вокзальная\"  NOT NULL,
    line            INTEGER         DEFAULT 2               NOT NULL,

    sql             TEXT,
    rank            INTEGER         DEFAULT 0               NOT NULL,
    process         TEXT,
    is_banned       BOOL            DEFAULT False           NOT NULL,
    lastseen        DATETIME        DEFAULT 0               NOT NULL,
    register_date   DATETIME        DEFAULT 0               NOT NULL,
    last_fight      DATETIME        DEFAULT 0               NOT NULL,
    prison_started  DATETIME        DEFAULT 0               NOT NULL,

    walrus          INTEGER         DEFAULT 0               NOT NULL,
    lootbox         INTEGER         DEFAULT 0               NOT NULL,
    cow             INTEGER         DEFAULT 0               NOT NULL,
    key             INTEGER         DEFAULT 0               NOT NULL,
    fox             INTEGER         DEFAULT 0               NOT NULL,
    gun             INTEGER         DEFAULT 0               NOT NULL,
    wolf            INTEGER         DEFAULT 0               NOT NULL,
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
    metro           INTEGER         DEFAULT 0               NOT NULL,
    traintoken      INTEGER         DEFAULT 0               NOT NULL,
    phone           INTEGER         DEFAULT 0               NOT NULL,
    troleytoken     INTEGER         DEFAULT 0               NOT NULL,
    hamster         INTEGER         DEFAULT 0               NOT NULL
)       
""")                       

def create_globaldata() -> None:
    cur.execute("""CREATE TABLE IF NOT EXISTS globaldata
(
    treasury        INTEGER         DEFAULT 0               NOT NULL,
    lastfill        DATETIME        DEFAULT 0               NOT NULL,
    baguette        INTEGER,
    pelmeni         INTEGER,
    soup            INTEGER,
    meat_on_bone    INTEGER,
    pita            INTEGER,
    tea             INTEGER
)""")

def create_clandata() -> None:
    cur.execute("""CREATE TABLE IF NOT EXISTS clandata
(
    id              INTEGER         PRIMARY KEY,
    clan_id         INTEGER, 
    clan_name       TEXT,
    clan_type       TEXT            DEFAULT \"public\"      NOT NULL,
    clan_balance    INTEGER         DEFAULT 0               NOT NULL,
    owner_id        INTEGER,
    HQ_place        TEXT        DEFAULT \"не установлено\"  NOT NULL,
    link            TEXT,
    lootbox         INTEGER         DEFAULT 0               NOT NULL,
    last_box        DATETIME        DEFAULT 0               NOT NULL, 
    description     TEXT,
    photo_id        TEXT
)
    """)

async def insert_clan(chat: Chat, user: User = {'id': None}) -> str:
    '''
    inserts chat into clandata 

    :param chat - chat that will be inserted 
    :param user - (Optional) clan creator
    
    :returns - new chat invite link
    '''

    link = await bot.create_chat_invite_link(chat.id, name='Jivopolis Default Invite Link')
    cur.execute(f"INSERT INTO clandata(clan_id, clan_name, owner_id, link) VALUES \
    ({chat.id}, '{chat.title}', '{user['id']}', '{link.invite_link}')")
    conn.commit()
    return link.invite_link
    
def insert_user(user: User) -> None:
    logger.info("user inserted")
    name = user.full_name
    login_id = encode_payload(user.id)
    cur.execute(f"INSERT INTO userdata(user_id, nickname, login_id) VALUES ({user.id}, \"{name}\", \"{login_id}\")")
    conn.commit()


"""lastfarm ???
    sql ???
    last_played???
    last_play??? WHY TWO
    refid???
    lastmath
    lastelec
    electimes???
    
    <<< flightach >>>"""


