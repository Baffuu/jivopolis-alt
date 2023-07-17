from dataclasses import dataclass


@dataclass
class ClanBuilding():
    name: str
    ru_name: str
    price: int = 0

    # how much each upgrade is more expensive than previous
    upgrade_markup: int = 0

    # the greatest level the building can be upgraded to
    # if 0, the building can't be upgraded
    max_level: int = 0

    # only admins can open the building
    admins_only: bool = False


CLAN_BUILDINGS = {

}
'''Store all available clan buildings'''
