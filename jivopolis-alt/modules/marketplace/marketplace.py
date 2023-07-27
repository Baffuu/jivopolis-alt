import random
import time
from datetime import datetime
from fyCursor import fyCursor, Table
from typing import Self, List

from ...database import tables, cur
from .constants import (
    ID,
    TABLE,
    SELLER_ID,
    COST,
    TYPE,
    PUT_UP_DATE,
    TEMP_ID,
    TEMP_ID_LENGTH,
    ALPHABET
)
from ...items import Item, ITEMS


class Product:
    """
    Represents product in marketplace
    """
    def __init__(
        self,
        id: int,
        owner_id: int,
        type: str,
        item: Item,
        cost: float | int,
        date: datetime
    ) -> None:
        self.id = id
        self.owner = owner_id
        self.type = type
        self.item = item
        self.cost = cost
        self.date = date

    def remove(self) -> Self:
        return market.remove(self)

    def check_time(self, time_: float) -> bool:
        return self.date + time_ < time.time()


class Marketplace:
    def __init__(
        self: Self,
        cursor: fyCursor,
        table: Table
    ) -> None:
        self.cur = cursor
        self.table = table

    def publish(
        self: Self,
        seller_id: int,
        item: Item | str,
        cost: float | int,
        temp_id: str
    ) -> int:
        self.table << {
            TYPE: item.name if isinstance(item, Item) else item,
            SELLER_ID: seller_id,
            PUT_UP_DATE: time.time(),
            COST: cost,
            TEMP_ID: temp_id
        }
        return self.get_by_temp(temp_id)

    def generate_temp(self):
        return "".join(random.choice(ALPHABET) for _ in range(TEMP_ID_LENGTH))  # todo: check if this id already exists # noqa: E501

    def get_by_temp(self, temp_id: str | int) -> int:
        out = self.cur.select("id", self.table.name).where(
            temp_id=temp_id).one()
        if out is None:
            raise RuntimeError("No item with such id")
        return out

    def remove(
        self: Self,
        product: int | float | Product | list[int | float | Product],
        *products: int | float | Product
    ) -> Product:
        if isinstance(product, list):
            for product_ in product:
                self.remove(product_)
        elif products:
            for product_ in products:
                self.remove(product_)

        if isinstance(product, (int, float)):
            product_id = product
        elif isinstance(product, Product):
            product_id = product.id
        else:
            raise TypeError("Wrong type of product")
        _product = self.get_product(product_id)
        self.cur.execute(f"DELETE FROM {self.table.name}\
                         WHERE id={product_id}").commit()
        return _product

    def get_product(
        self: Self,
        product_id: int
    ) -> Product:
        if not self.cur.select("COUNT(*)", TABLE).where(id=product_id).one():
            raise ValueError("Product with such id does not exists")
        name = self.cur.select(TYPE, TABLE).where(id=product_id).one()
        stamp = float(self.cur.select(PUT_UP_DATE, TABLE).where(
            id=product_id).one())
        time = datetime.fromtimestamp(stamp)
        return Product(
            product_id,
            self.cur.select(SELLER_ID, TABLE).where(id=product_id).one(),
            name,
            ITEMS[name],
            self.cur.select(COST, TABLE).where(id=product_id).one(),
            time
        )

    def get_all(self: Self) -> List[Product]:
        ids = self.cur.select(ID, TABLE).fetch()

        output = []

        for tuple_ in ids:
            output.extend(self.get_product(id) for id in tuple_)
        return output


market = Marketplace(cur, tables[TABLE])
