import datetime
import re
import typing

from bson import ObjectId
from bson.tz_util import utc

from rethink import config, const
from . import user, tps, utils, db_ops
from .database import COLL

AT_PTN = re.compile(r'\[@[\w ]+?]\(([\w/]+?)\)', re.MULTILINE)
TITLE_PTN = re.compile(r'^#*?\s*?(.+?)\s*$', re.MULTILINE)
CURSOR_AT_PTN = re.compile(r'\s+?@([\w ]*)$')


def __get_linked_nodes(new_text) -> typing.Tuple[set, const.Code]:
    # last first
    cache_current_to_nid: typing.Set[str] = set()

    for match in list(AT_PTN.finditer(new_text))[::-1]:
        l0, l1 = match.span(1)
        link = new_text[l0:l1]
        if link.startswith("/node/"):
            # check existed nodes
            to_nid = link[6:]
            cache_current_to_nid.add(to_nid)
    return cache_current_to_nid, const.Code.OK


def __remove_from_nodes(
        nid: str,
        to_node_ids: typing.List[str],
        cache_current_to_nid: set
):
    orig_current_to_nid = set(to_node_ids)
    # remove fromNodes for linked nodes
    for to_nid in orig_current_to_nid.difference(cache_current_to_nid):
        db_ops.remove_from_node(from_nid=nid, to_nid=to_nid)


def __flush_to_node_ids(
        nid: str,
        to_node_ids: typing.List[str],
        new_text: str
) -> typing.Tuple[typing.List[str], const.Code]:
    cache_current_to_nid, code = __get_linked_nodes(new_text=new_text)
    if code != const.Code.OK:
        return [], code

    __remove_from_nodes(nid=nid, to_node_ids=to_node_ids, cache_current_to_nid=cache_current_to_nid)

    return list(cache_current_to_nid), const.Code.OK


def __verify_title(title: str) -> bool:
    if title == "":
        return True
    found = TITLE_PTN.match(title)
    if found is None:
        return False
    return True


def add(
        uid: str,
        title: str,
        text: str,
        type_: int = const.NodeType.MARKDOWN.value,
        from_nid: str = "",
) -> typing.Tuple[typing.Optional[tps.Node], const.Code]:
    title = title.strip()
    if __verify_title(title=title) is False:
        return None, const.Code.INVALID_TITLE
    text = text.strip()
    onid = utils.short_uuid()

    from_nids = []
    if from_nid != "":
        from_nids.append(from_nid)
        res = db_ops.node_add_to_set(from_nid, "toNodeIds", onid)
        if res.modified_count != 1:
            return None, const.Code.OPERATION_FAILED

    new_to_node_ids = []
    if text != "":
        new_to_node_ids, code = __flush_to_node_ids(nid=onid, to_node_ids=[], new_text=text)
        if code != const.Code.OK:
            return None, code
    _id = ObjectId()
    data: tps.Node = {
        "_id": _id,
        "id": onid,
        "title": title,
        "text": text,
        "snippet": utils.md2txt(text=text)[:200],
        "type": type_,
        "disabled": False,
        "modifiedAt": _id.generation_time,
        "fromNodeIds": from_nids,
        "toNodeIds": new_to_node_ids,
        "fromNodes": [],
        "toNodes": [],
        "searchKeys": utils.text2search_keys(title),
    }
    res = COLL.nodes.insert_one(data)
    if not res.acknowledged:
        return None, const.Code.OPERATION_FAILED
    res = COLL.users.update_one(
        {"id": uid},
        {"$push": {"nodeIds": onid}}
    )
    if res.modified_count != 1:
        return None, const.Code.OPERATION_FAILED

    return data, const.Code.OK


def __set_linked_nodes(doc: tps.Node):
    doc["fromNodes"] = list(COLL.nodes.find({"id": {"$in": doc["fromNodeIds"]}}))
    doc["toNodes"] = list(COLL.nodes.find({"id": {"$in": doc["toNodeIds"]}}))


def get(
        uid: str,
        nid: str,
        with_disabled: bool = False,
) -> typing.Tuple[typing.Optional[tps.Node], const.Code]:
    u, code = user.get(uid=uid)
    if code != const.Code.OK:
        return None, code
    if nid not in u["nodeIds"]:
        return None, const.Code.NODE_NOT_EXIST
    assert_conditions = {} if with_disabled else {"disabled": False}
    doc = db_ops.node_get(id_=nid, assert_conditions=assert_conditions)
    if doc is None:
        return None, const.Code.NODE_NOT_EXIST

    __set_linked_nodes(doc=doc)
    return doc, const.Code.OK


def update(
        uid: str,
        nid: str,
        title: str = "",
        text: str = "",
) -> typing.Tuple[typing.Optional[tps.Node], const.Code]:
    title = title.strip()
    if __verify_title(title=title) is False:
        return None, const.Code.INVALID_TITLE
    text = text.strip()

    if not user.is_exist(uid=uid):
        return None, const.Code.ACCOUNT_OR_PASSWORD_ERROR
    n, code = get(uid=uid, nid=nid)
    if code != const.Code.OK:
        return None, code
    if n["title"] == title and n["text"] == text:
        return n, const.Code.OK
    new_data = {"title": title, "searchKeys": utils.text2search_keys(title), }
    if text != "":
        new_data["toNodeIds"], code = __flush_to_node_ids(
            nid=n["id"], to_node_ids=n["toNodeIds"], new_text=text)
        if code != const.Code.OK:
            return None, code
        new_data["text"] = text
        new_data["snippet"] = utils.md2txt(text=text)[:200]
    new_data["modifiedAt"] = datetime.datetime.now(tz=utc)

    if not config.is_local_db():
        doc = COLL.nodes.find_one_and_update(
            {"id": nid},
            {"$set": new_data},
            return_document=True,   # return updated doc
        )
    else:
        res = COLL.nodes.update_one(
            {"id": nid},
            {"$set": new_data}
        )
        if res.modified_count != 1:
            return None, const.Code.OPERATION_FAILED
        doc = COLL.nodes.find_one({"id": nid})

    if doc is None:
        return None, const.Code.NODE_NOT_EXIST
    __set_linked_nodes(doc=doc)
    return doc, const.Code.OK


def get_cursor_text_recommend(
        uid: str,
        nid: str,
        cursor_text: str,
) -> typing.Tuple[typing.Optional[str], typing.List[tps.Node]]:
    if cursor_text.startswith("@"):
        query = cursor_text[1:].strip()
    else:
        found = CURSOR_AT_PTN.search(cursor_text)
        if found is None:
            return None, []
        query = found.group(1).strip()

    if query == "":
        u = COLL.users.find_one({"id": uid})
        if u is None:
            return query, []
        rn = u["recentAtSearchedNodeIds"]
        try:
            rn.remove(nid)
        except ValueError:
            pass
        return query, list(COLL.nodes.find({"id": {"$in": rn}}))
    return query, search_user_node(
        uid=uid,
        query=query,
        sort_key="modifiedAt",
        sort_order=-1,
        page=0,
        page_size=8,
        nid_exclude=[nid],
    )


def delete(uid: str, nid: str) -> const.Code:
    n, code = get(uid=uid, nid=nid, with_disabled=True)
    if code != const.Code.OK:
        return code

    # remove fromNodes for linked nodes
    for linked_nid in n["fromNodeIds"]:
        db_ops.remove_to_node(from_nid=linked_nid, to_nid=nid)

    # remove toNodes for linked nodes
    for linked_nid in n["toNodeIds"]:
        db_ops.remove_from_node(from_nid=nid, to_nid=linked_nid)

    # remove node
    res = COLL.nodes.delete_one({"id": nid})
    if res.deleted_count != 1:
        return const.Code.OPERATION_FAILED

    # update user nodeIds
    res = db_ops.user_node_pull(uid, "nodeIds", nid)
    if res.matched_count != 1:
        return const.Code.OPERATION_FAILED

    return const.Code.OK


def disable(
        uid: str,
        nid: str,
) -> const.Code:
    if not user.is_exist(uid=uid):
        return const.Code.ACCOUNT_OR_PASSWORD_ERROR
    res = COLL.nodes.update_one(
        {"id": nid},
        {"$set": {"disabled": True}}
    )
    if res.modified_count != 1:
        return const.Code.OPERATION_FAILED
    return const.Code.OK


def search_user_node(
        uid: str,
        query: str = "",
        sort_key: str = "createAt",
        sort_order: int = -1,
        page: int = 0,
        page_size: int = 0,
        nid_exclude: typing.Sequence[str] = None,
) -> typing.List[tps.Node]:
    u = COLL.users.find_one({"id": uid})
    if u is None:
        return []

    if nid_exclude is None or len(nid_exclude) == 0:
        nids = u["nodeIds"]
    else:
        nid_exclude = nid_exclude or []
        nid_exclude = set(nid_exclude)
        nids = set(u["nodeIds"])
        nids.difference_update(nid_exclude)
        nids = list(nids)

    condition = {
        "id": {"$in": nids},
        "disabled": False,
    }
    query = query.strip()

    # on remote mongodb
    if query != "" and not config.is_local_db():
        condition["$or"] = [
            {"searchKeys": {"$regex": query}},
            {"text": {"$regex": query}},
        ]

    docs = COLL.nodes.find(condition)

    if sort_key != "":
        if sort_key == "createAt":
            sort_key = "_id"
        elif sort_key == "similarity":
            sort_key = "_id"  # TODO: sort by similarity
        docs = docs.sort(sort_key, direction=sort_order)

    if page_size > 0:
        docs = docs.skip(page * page_size).limit(page_size)

    if config.is_local_db() and query != "":
        return [doc for doc in docs if query in doc["searchKeys"] or query in doc["text"]]
    return list(docs)


def cursor_node_selected(
        uid: str,
        nid: str,
        to_nid: str,
) -> const.Code:
    # add selected node to recentAtSearchedNodeIds
    c = {"id": uid}
    if not config.is_local_db():
        c.update({"disabled": False, "nodeIds": {"$in": [nid, to_nid]}})

    doc = COLL.users.find_one(c)
    if doc is None:
        return const.Code.ACCOUNT_OR_PASSWORD_ERROR

    if config.is_local_db():
        if doc["disabled"]:
            return const.Code.ACCOUNT_OR_PASSWORD_ERROR
        if nid not in doc["nodeIds"] or to_nid not in doc["nodeIds"]:
            return const.Code.NODE_NOT_EXIST

    rns = doc["recentAtSearchedNodeIds"]
    if to_nid in rns:
        rns.remove(to_nid)
    rns.insert(0, to_nid)
    if len(rns) > 10:
        rns = rns[:10]

    # add to recentAtSearchedNodeIds
    res = COLL.users.update_one(
        {"id": uid},
        {"$set": {"recentAtSearchedNodeIds": rns}}
    )
    if res.modified_count != 1:
        return const.Code.OPERATION_FAILED

    return const.Code.OK


def new_user_add_default_nodes(language: str, uid: str) -> const.Code:
    lns = const.NEW_USER_DEFAULT_NODES[language]
    n, code = add(
        uid=uid,
        title=lns[0]["title"],
        text=lns[0]["text"],
    )
    if code != const.Code.OK:
        return code
    _, code = add(
        uid=uid,
        title=lns[1]["title"],
        text=lns[1]["text"].format(n["id"]),
    )
    return code
