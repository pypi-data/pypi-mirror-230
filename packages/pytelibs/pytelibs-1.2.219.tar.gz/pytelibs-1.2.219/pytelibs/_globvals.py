# pytel < https://t.me/kastaid >
# Copyright (C) 2023-present kastaid
#
# This file is a part of < https://github.com/kastaid/pytel/ >
# Please read the GNU Affero General Public License in
# < https://github.com/kastaid/pytel/blob/main/LICENSE/ >.

from typing import Set


_GCAST_LOCKED: Set[int] = set()
_GUCAST_LOCKED: Set[int] = set()
_GBAN_LOCKED: Set[int] = set()
_UNGBAN_LOCKED: Set[int] = set()
_INVITED_LOCKED: Set[int] = set()
_KICKED_LOCKED: Set[int] = set()

SETMODE_ONLINE: Set[int] = set()
SETMODE_OFFLINE: Set[int] = set()

LOCK_TYPES: dict = {
    "all": "Everything.",
    "messages": "Text, contacts, locations and venues.",
    "media": "Audio files, documents, photos, videos, video notes and voice notes.",
    "others": "Stickers, games, gifs, inline.",
    "links": "Web priview.",
    "polls": "Polling.",
    "info": "Change info.",
    "invite": "Invite users.",
    "pin": "Pinned messages.",
}

_CHARACTER_NAMES = {
    "`": "",
    "*": "",
    "_": "",
    "-": "",
    "~": "",
    "/": "",
    "|": "",
    "[": "",
    "]": "",
    "<": "",
    ">": "",
    "'": "",
    "{": "",
    "}": "",
    ")": "",
    "(": "",
    "’": "",
    "‘": "",
    "=": "",
    "#": "",
    "&": "",
    "+": "",
    "^": "",
    "%": "",
    "°": "",
    ";": "",
    ":": "",
    "?": "",
    "!": "",
    "@": "",
    "¡": "",
    "¿": "",
    "‽": "",
    "♪": "",
    "±": "",
    '″': '',
    "‚": "",
    ".": "",
    "№": "",
    "—": "",
    "–": "",
    "·": "",
}

SIZE_UNITS = [
    "B",
    "KB",
    "MB",
    "GB",
    "TB",
    "PB",
    "EB",
]
