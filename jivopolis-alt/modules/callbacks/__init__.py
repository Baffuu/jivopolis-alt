# flake8: noqa
from .other import (
    chats, my_refferals,
    get_cheque, cellphone_menu,
    give_state, economics, toggle_nonick,
    user_settings, exchange_center, exchange_, exchange_menu_
)

from .for_admins import (
    adminpanel, itemsinfo_table,
    itemsinfo_item, adminhelp,
    sqlapprove, sqldecline,
    restart, adminchats
)

from .inventory import (
    itemdesc, inventory,
    lootbox_button, sellitem,
    resources, sellresource
)

from .user_profile import (
    set_user_bio, put_mask_off,
    put_mask_on, my_reflink,
    privacy_settings
)

from .traveling import (
    buycall, city, car_menu,
    goto_on_car, local_people,
    delivery_menu,
    central_market_menu,
    central_market_food,
    bank, state_balance,
    taxi_menu, taxicost,
    taxi_goto_, gps_menu,
    central_market_mask, buy24_,
    buyclan_,
    bus, railway_station,
    taxi_page,
    metro, proceed_metro,
    metrocall, metro_forward,
    metro_back, transfer_metro,
    airport, flight, regtrain_lounge,
    regtraincall, regtrain_back, regtrain_forward,
    proceed_regtrain, trolleybuscall, trolleybus_lounge,
    proceed_trolleybus, trolleybus_back, trolleybus_forward,
    businessclass_lounge, go_bytrain, buscall, regbuscall,
    go_bybus, go_byshuttle, tramcall, tram_lounge, proceed_tram,
    tram_forward, tram_back, walk, gps_category, gps_location,
    gps_transport, car_menu_page, local_clans, find_address,
    search_by_address
)

from .locations import (
    farm, milk_cow, mineshaft, go_mining, resource_market,
    factory, play_gears, answer_gears, university, play_math,
    answer_math, play_geo, answer_geo
)

from .clans import (
    create_clan, joinclan, leaveclan, clan_members, call_clan,
    clan_top, clan_settings, delete_clan, delete_clan_confirm,
    toggle_clan_type, clan_hq, set_clan_name, set_clan_bio,
    confirm_clan_profile_setting, delete_clan_bio, clan_profile,
    set_clan_link, delete_clan_link, delete_clan_name, confirm_clan_photo,
    set_clan_photo, delete_clan_photo, clan_addon_menu, buy_clan_addon,
    sell_clan_addon, clan_features, set_gameclub_timeout, confirm_timeout,
    clan_filter, toggle_filter, clan_buildings, clan_building_shop,
    buy_clan_building, sell_clan_building, upgrade_clan_building, clan_building_menu,
    use_clan_building, donate_cow, milk_cow_clan, give_lootboxes
)

from .shops import (
    mall,
    shop_24,
    shop,
    moda_menu,
    ticket_shop,
    maximdom, maximdom_elevator
)
