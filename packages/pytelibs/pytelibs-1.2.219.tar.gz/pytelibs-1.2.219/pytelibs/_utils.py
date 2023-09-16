# pytel < https://t.me/kastaid >
# Copyright (C) 2023-present kastaid
#
# This file is a part of < https://github.com/kastaid/pytel/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/pytel/blob/main/LICENSE/ >.

import re
from functools import reduce


def replace_all(
    text: str,
    repls: dict,
    regex: bool = False,
) -> str:
    if regex:
        return reduce(
            lambda a, kv: re.sub(*kv, a, flags=re.I),
            repls.items(),
            text
        )
    return reduce(
        lambda a, kv: a.replace(*kv),
        repls.items(),
        text
    )


def normalize_youtube_url(
    url: str
) -> str:
    if not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    host = url.split("//")[-1].split("/")[0].split("?")[0]
    repls = {
        host: host.lower(),
        "m.": "",
        "music.": "",
        "youtube-nocookie": "youtube",
        "shorts/": "watch?v=",
        "embed/": "watch?v=",
    }
    return replace_all(
        url,
        repls
    ).split("&")[0]


def is_youtube_url(
    url: str
) -> bool:
    pattern = r"^(?:https?://)?((www|m|music)\.|)((youtu\.be/.+)|((youtube|youtube-nocookie)\.com/(watch\?v=|shorts/|embed/).+))$"
    return bool(
        re.match(
            pattern,
            url,
            flags=re.I
        )
    )


def converting_binnary(
    data: str,
    convert: bool= None,
):
    if convert:
        binnary = " ".join(
            format(x, "08b")
            for x in bytearray(
                data, "utf-8"
            )
        )
    else:
        a = "".join(data)
        number = a.split()
        binnary = "".join(
            chr(int(binary, 2))
            for binary in number
        )

    return binnary
