from dataclasses import dataclass


@dataclass
class ClanBuilding():
    name: str
    ru_name: str
    description: str
    price: int = 0

    # how much each upgrade is more expensive than previous
    upgrade_markup: int = 0

    # the greatest level the building can be upgraded to
    # if 0, the building can't be upgraded
    max_level: int = 0

    # only admins can open the building
    admins_only: bool = False


CLAN_BUILDINGS = {
    'mail': ClanBuilding(
        name='mail',
        ru_name='📦 Почтовое отделение',
        description=(
            'хороший способ обеспечивать всеех участников клана лутбоксами'
            ' еженедельно'
        ),
        price=700,
        upgrade_markup=100,
        max_level=50,
        admins_only=True
    ),
    'canteen': ClanBuilding(
        name='canteen',
        ru_name='🍲 Столовая',
        description=(
            'участникам - дешёвая еда, клану - деньги :)'
        ),
        price=500,
        upgrade_markup=0,
        max_level=0
    ),
    'pharmacy': ClanBuilding(
        name='pharmacy',
        ru_name='💊 Аптека',
        description=(
            'лекарства дешевле, чем в больнице'
        ),
        price=600,
        upgrade_markup=0,
        max_level=0
    ),
    'farm': ClanBuilding(
        name='farm',
        ru_name='🌾 Ферма',
        description=(
            'дайте участникам возможность доить своих коров'
        ),
        price=600,
        upgrade_markup=0,
        max_level=0
    )
}
'''Store all available clan buildings'''
