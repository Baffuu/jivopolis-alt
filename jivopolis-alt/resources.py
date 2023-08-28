from dataclasses import dataclass


@dataclass
class Resource():
    name: str
    ru_name: str
    chance: int = 1  # chance of at least one resource to be mined
    maximum: int = 1  # maximum amount to be mined per one digging
    cost: int = -1


RESOURCES = {
    'cobble': Resource(
        name='cobble',
        ru_name='Булыжник',
        chance=0.75,
        maximum=9,
        cost=10
    ),
    'coal': Resource(
        name='coal',
        ru_name='Уголь',
        chance=0,
        maximum=0,
        cost=34
    ),
    'iron': Resource(
        name='iron',
        ru_name='Железо',
        chance=0.1,
        maximum=5,
        cost=50
    ),
    'gold': Resource(
        name='gold',
        ru_name='Золото',
        chance=0.05,
        maximum=3,
        cost=200
    ),
    'gem': Resource(
        name='gem',
        ru_name='Алмаз',
        chance=0.01,
        maximum=2,
        cost=450
    ),
    'topaz': Resource(
        name='topaz',
        ru_name='Топаз',
        chance=0.005,
        maximum=1,
        cost=750
    )
}
'''Store all resources which are mined in Gorny mineshaft'''
