# type: ignore
# flake8: noqa
import time
import random

from .misc import tglog, ITEMS
from .database import cur
from .misc.config import limeteds

from loguru import logger


async def update():
    await refill_market()
    await update_crypto()


async def refill_market():
    lastfill = time.time() - cur.execute(
        "SELECT lastfill FROM globaldata"
    ).fetchone()[0]

    if lastfill < 86400:  # 1 day
        return
    for item in limeteds:
        cur.execute(
            f"UPDATE globaldata SET {item}={random.randint(5, 15)}"
        )
    cur.execute(f"UPDATE globaldata SET lastfill={time.time()}")
    logger.info("Market was refilled succesfully")
    await tglog(
        "🚐 Круглосуточный магазин был только что восполнен.",
        "#market_refill"
    )


async def update_crypto():
    lastupdate = time.time() - cur.execute(
        "SELECT lastcrypto FROM globaldata"
    ).fetchone()[0]

    if lastupdate < 60 * 60 * 4:  # 4 hours
        return

    crypto = await get_crypto()

    for c in crypto:
        try:
            current_value = cur.execute(
                f"SELECT value FROM cryptodata WHERE crypto=\"{c}\""
            ).fetchone()[0]
        except TypeError:
            current_value = 0

        change = random.randint(-500, 650)

        if current_value + change <= 5:
            change = random.randint(0, 650)

        _change_values(c, current_value, change)

    cur.execute(f"UPDATE globaldata SET lastcrypto={time.time()}")
    logger.info("Cryptocurrency value was changed succesfully")
    await tglog("📊 Курс криптовалюты изменился.", "#crypto_change")


def _change_values(c, current_value, change):
    prev_value = cur.select("prev_value", from_="cryptodata").where(
        crypto=c
    ).one()
    hours_8 = cur.select("hours_8", from_="cryptodata").where(crypto=c).one()
    hours_12 = cur.select("hours_12", from_="cryptodata").where(crypto=c).one()
    hours_16 = cur.select("hours_16", from_="cryptodata").where(crypto=c).one()
    hours_20 = cur.select("hours_20", from_="cryptodata").where(crypto=c).one()

    cur.update("cryptodata").add(value=change).where(
        crypto=c
    ).commit()
    cur.update("cryptodata").set(prev_value=current_value).where(
        crypto=c
    ).commit()
    cur.update("cryptodata").set(hours_8=prev_value).where(crypto=c).commit()
    cur.update("cryptodata").set(hours_12=hours_8).where(crypto=c).commit()
    cur.update("cryptodata").set(hours_16=hours_12).where(crypto=c).commit()
    cur.update("cryptodata").set(hours_20=hours_16).where(crypto=c).commit()
    cur.update("cryptodata").set(hours_24=hours_20).where(crypto=c).commit()


async def get_crypto() -> list:
    return [item for item in ITEMS if ITEMS[item].type == "crypto"]
