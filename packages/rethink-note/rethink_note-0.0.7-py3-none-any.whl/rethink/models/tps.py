import datetime
import typing as tp

from bson import ObjectId
from typing_extensions import TypedDict


class LinkedNode(TypedDict):
    _id: ObjectId
    id: str
    title: str
    text: str
    type: int  # const.NodeType.MARKDOWN.value
    disabled: bool
    modifiedAt: datetime.datetime


class Node(TypedDict):
    _id: ObjectId
    id: str
    title: str
    searchKeys: str
    text: str
    snippet: str
    type: int  # const.NodeType.MARKDOWN.value
    disabled: bool
    modifiedAt: datetime.datetime
    fromNodeIds: tp.List[str]
    toNodeIds: tp.List[str]
    fromNodes: tp.Optional[tp.List[LinkedNode]]
    toNodes: tp.Optional[tp.List[LinkedNode]]


class User(TypedDict):
    _id: ObjectId
    id: str
    source: int
    account: str
    nickname: str
    email: str
    avatar: str
    hashed: str
    disabled: bool
    nodeIds: tp.List[str]
    modifiedAt: datetime.datetime
    recentAtSearchedNodeIds: tp.List[str]
    language: str
