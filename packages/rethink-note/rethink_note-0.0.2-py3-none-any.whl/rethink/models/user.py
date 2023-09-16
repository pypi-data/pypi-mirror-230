import datetime
import typing

from bson import ObjectId
from bson.tz_util import utc

from rethink import const
from . import tps, utils
from .database import COLL


def add(
        account: str,
        source: int,
        email: str,
        hashed: str,
        nickname: str,
        avatar: str,
        language: str,
) -> typing.Tuple[str, const.Code]:
    if COLL.users.find_one({"account": account, "source": source}) is not None:
        return "", const.Code.EMAIL_OCCUPIED
    oid = ObjectId()
    # assert language in const.Language
    if not const.Language.is_valid(language):
        language = const.Language.EN.value
    data: tps.User = {
        "_id": oid,
        "id": utils.short_uuid(),
        "account": account,
        "source": source,
        "email": email,
        "hashed": hashed,
        "avatar": avatar,
        "disabled": False,
        "nickname": nickname,
        "modifiedAt": oid.generation_time,
        "nodeIds": [],
        "recentAtSearchedNodeIds": [],
        "language": language,
    }
    res = COLL.users.insert_one(data)
    if not res.acknowledged:
        return "", const.Code.OPERATION_FAILED
    return data["id"], const.Code.OK


def update(
        uid: str,
        email: str = "",
        hashed: str = "",
        nickname: str = "",
        avatar: str = "",
        language: str = "",
) -> const.Code:
    u, code = get(uid=uid)
    if code != const.Code.OK:
        return code
    email = email.strip()
    if email not in ["", u["email"]] and COLL.users.find_one(
            {"account": email, "source": const.UserSource.EMAIL.value}
    ) is not None:
        return const.Code.EMAIL_OCCUPIED
    if email == "":
        email = u["email"]
    hashed = hashed.strip()
    if hashed == "":
        hashed = u["hashed"]
    nickname = nickname.strip()
    if nickname == "":
        nickname = u["nickname"]
    avatar = avatar.strip()
    if avatar == "":
        avatar = u["avatar"]
    language = language.strip()
    if language == "":
        language = u["language"]
    elif not const.Language.is_valid(language):
        return const.Code.INVALID_LANGUAGE

    res = COLL.users.update_one(
        {"id": uid},
        {"$set": {
            "email": email,
            "hashed": hashed,
            "nickname": nickname,
            "avatar": avatar,
            "modifiedAt": datetime.datetime.now(tz=utc),
            "language": language,
        }}
    )
    return const.Code.OK if res.modified_count == 1 else const.Code.OPERATION_FAILED


def delete(uid: str) -> const.Code:
    res = COLL.users.delete_one({"id": uid})
    return const.Code.OK if res.deleted_count == 1 else const.Code.OPERATION_FAILED


def disable(uid: str) -> const.Code:
    res = COLL.users.update_one(
        {"id": uid},
        {"$set": {"disabled": True}}
    )
    return const.Code.OK if res.modified_count == 1 else const.Code.OPERATION_FAILED


def enable(uid: str) -> const.Code:
    res = COLL.users.update_one(
        {"id": uid},
        {"$set": {"disabled": False}}
    )
    return const.Code.OK if res.modified_count == 1 else const.Code.OPERATION_FAILED


def get_by_email(email: str) -> typing.Tuple[typing.Optional[tps.User], const.Code]:
    return get_account(account=email, source=const.UserSource.EMAIL.value)


def get_account(account: str, source: int) -> typing.Tuple[typing.Optional[tps.User], const.Code]:
    u = COLL.users.find_one({"source": source, "account": account, "disabled": False})
    if u is None:
        return None, const.Code.ACCOUNT_OR_PASSWORD_ERROR
    return u, const.Code.OK


def get(uid: str) -> typing.Tuple[typing.Optional[tps.User], const.Code]:
    u = COLL.users.find_one({"id": uid, "disabled": False})
    if u is None:
        return None, const.Code.ACCOUNT_OR_PASSWORD_ERROR
    return u, const.Code.OK


def get_hash_by_uid(uid: str) -> typing.Optional[str]:
    u = COLL.users.find_one({"id": uid, "disabled": False})
    if u is None:
        return None
    return u["hashed"]


def is_exist(uid: str) -> bool:
    try:
        COLL.users.find({"id": uid, "disabled": False}, limit=1).next()
    except StopIteration:
        return False
    return True
