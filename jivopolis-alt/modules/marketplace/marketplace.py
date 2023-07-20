import time
from dataclasses import dataclass
from datetime import datetime
from fyCursor import fyCursor, Table
from typing import Union, Self, List, get_args

from ...database import tables, cur
from .constants import ID, TABLE, SELLER_ID, COST, TYPE, PUT_UP_DATE
from ...items import Item, ITEMS


@dataclass
class Product:
    id: int
    owner_id: int
    type: str
    item: Item
    cost: float | int
    date: datetime

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
        cost: float | int
    ) -> None:
        self.table << {
            TYPE: item.name if isinstance(item, Item) else item,
            SELLER_ID: seller_id,
            PUT_UP_DATE: time.time(),
            COST: cost
        }

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

        if isinstance(product, get_args(Union[int, float])):
            product_id = product
        elif isinstance(product, Product):
            product_id = product.id
        else:
            raise TypeError("Wrong type of product")
        _product = self.get_product(product_id)
        self.cur.execute(f"DELETE FROM {TABLE} WHERE id={product_id}").commit()
        return _product

    def get_product(
        self: Self,
        product_id: int
    ) -> Product:
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

        def unpack(to_unpack: list[tuple[int]]) -> list[int]:
            output = []

            for tuple_ in to_unpack:
                for element in tuple_:
                    output.append(element)

            return output

        output = []

        for id in unpack(ids):
            output.append(self.get_product(id))
        return output


market = Marketplace(cur, tables[TABLE])
