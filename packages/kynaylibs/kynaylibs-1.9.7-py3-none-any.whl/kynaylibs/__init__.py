import sys

import kymang
from kymang import *

BL_GCAST = [
    -1001599474353,
    -1001692751821,
    -1001473548283,
    -1001459812644,
    -1001433238829,
    -1001476936696,
    -1001327032795,
    -1001294181499,
    -1001419516987,
    -1001209432070,
    -1001296934585,
    -1001481357570,
    -1001459701099,
    -1001109837870,
    -1001485393652,
    -1001354786862,
    -1001109500936,
    -1001387666944,
    -1001390552926,
    -1001752592753,
    -1001777428244,
    -1001771438298,
    -1001287188817,
    -1001812143750,
    -1001883961446,
    -1001753840975,
    -1001896051491,
    -1001578091827,
    -1001284445583,
    -1001927904459,
    -1001675396283,
]


DEVS = [
    1898065191,  # @rizzvbss
    1054295664,  # @kenapanan
    1889573907,  # @kanaayyy
    1755047203,  # @Bangjhorr
    2133148961,  # @mnaayyy
    2076745088,  # @gua
    5876222922,  # Tomay
    1936017380,  # otan
    2013365169,  # liona
    1966129176,  # doms
    5063062493,  # kazu
    1939171309,  # doni
    1810243126,  # om
    1992087933,  # zen
    1993568296,  # cuki
    1839010591,  # amang
    2033762302,  # reza
    5573141376,  # rito
    1087819304,  # reja
]


async def ajg(client):
    try:
        await client.join_chat("kynansupport")
        await client.join_chat("kontenfilm")
        await client.join_chat("abtnaaa")
        await client.join_chat("PesulapTelegram")
    except kymang.errors.exceptions.bad_request_400.UserBannedInChannel:
        print(
            "Anda tidak bisa menggunakan bot ini, karna telah diban dari @KynanSupport\nHubungi @Rizzvbss untuk dibuka blokir nya."
        )
        sys.exit()
