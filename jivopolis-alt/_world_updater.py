import contextlib
import time
import random

from .misc import OfficialChats, tglog, ITEMS
from .database.sqlitedb import cur, conn
from .misc.config import limeteds

from loguru import logger

async def update():
    await refill_market()
    await update_crypto()


async def refill_market():  
    lastfill = time.time() - cur.execute("SELECT lastfill FROM globaldata").fetchone()[0]

    if lastfill >= 86400: # 1 day
        for item in limeteds:
            cur.execute(f"UPDATE globaldata SET {item}={random.randint(5, 15)}")
        cur.execute(f"UPDATE globaldata SET lastfill={time.time()}")
        logger.info("Market was refilled succesfully")
        await tglog("🚐 Круглосуточный магазин был только что восполнен.", "#market_refill")


async def update_crypto():
    lastupdate = time.time() - cur.execute("SELECT lastcrypto FROM globaldata").fetchone()[0]
    crypto = await get_crypto()
    if lastupdate >= 3600*4: # 4 hours
        for c in crypto:
            with contextlib.suppress(TypeError):
                crv = cur.execute(f"SELECT value FROM cryptodata WHERE crypto=\"{c}\"").fetchone()[0]
            change = random.randint(-500, 650)
            if crv+change <= 5:
                change = random.randint(0, 650)
            cur.execute(f"UPDATE cryptodata SET value = value+{change} WHERE crypto = \"{c}\"")
            conn.commit()
        cur.execute(f"UPDATE globaldata SET lastcrypto={time.time()}")
        logger.info("Cryptocurrency value was changed succesfully")
        await tglog("📊 Курс криптовалюты изменился.", "#crypto_change")

async def get_crypto() -> list:
    return [item for item in ITEMS if ITEMS[item].type == "crypto"]