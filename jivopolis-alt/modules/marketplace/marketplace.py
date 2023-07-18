import time
from fyCursor import fyCursor, Table
from ...database import tables, cur
from .constants import TABLE
from ...items import Item


class Marketplace:
    def __init__(
        self,
        cursor: fyCursor,
        table: Table
    ) -> None:
        self.cur = cursor
        self.table = table

    def publish(
        self,
        item: Item,
        seller_id: int,
        cost: float | int
    ):
        self.table << {
            "type": item.name,
            "seller_id": seller_id,
            "put_up_date": time.time(),
            "cost": cost
        }


market = Marketplace(cur, tables[TABLE])
