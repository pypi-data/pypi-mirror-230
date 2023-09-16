import typing
from dataclasses import dataclass, field

from rethink import const, models
from .base import AcknowledgeResponse, UidCode, datetime2str


@dataclass
class NodeData:
    @dataclass
    class LinkedNode:
        id: str
        title: str
        text: str
        snippet: str
        type: int
        disabled: bool
        createdAt: str
        modifiedAt: str
    id: str
    title: str
    text: str
    type: int
    disabled: bool
    createdAt: str
    modifiedAt: str
    fromNodes: typing.List[LinkedNode] = field(default_factory=list)
    toNodes: typing.List[LinkedNode] = field(default_factory=list)


@dataclass
class PutNodeRequest:
    fulltext: str
    type: int
    requestId: str = ""
    fromNid: str = ""


@dataclass
class PutNodeResponse:
    code: int
    message: str
    requestId: str
    node: typing.Optional[NodeData]


@dataclass
class GetNodeResponse:
    code: int
    message: str
    requestId: str
    node: typing.Optional[NodeData]


@dataclass
class SearchUserNodesRequest:
    requestId: str
    query: str = ""
    sortKey: str = "createAt"
    sortOrder: int = -1
    page: int = 0
    pageSize: int = 0
    nidExclude: typing.Sequence[str] = field(default_factory=list)


@dataclass
class NodesInfoResponse:
    @dataclass
    class NodeInfo:
        id: str
        title: str
        snippet: str
        type: int
        createdAt: str
        modifiedAt: str
    code: int
    message: str
    requestId: str
    nodes: typing.List[NodeInfo]


@dataclass
class UpdateNodeRequest:
    nid: str
    fulltext: str
    requestId: str = ""


@dataclass
class CursorQueryRequest:
    nid: str
    textBeforeCursor: str
    requestId: str = ""


@dataclass
class CursorQueryResponse:
    @dataclass
    class Result:
        nodes: typing.List[NodesInfoResponse.NodeInfo]
        query: typing.Optional[str]
    code: int
    message: str
    requestId: str
    result: typing.Optional[Result]


@dataclass
class CursorSearchSelectRequest:
    requestId: str
    nid: str
    toNid: str


def __split_title_text(text: str) -> (str, str):
    title_text = text.split("\n", maxsplit=1)
    title = title_text[0].strip()
    try:
        text = title_text[1].strip()
    except IndexError:
        text = ""
    return title, text


def put_resp(
        uc: UidCode,
        req: PutNodeRequest,
) -> PutNodeResponse:
    if uc.code != const.Code.OK:
        return PutNodeResponse(
            code=uc.code.value,
            message=const.get_msg_by_code(uc.code, uc.language),
            requestId=req.requestId,
            node=None
        )

    title, text = __split_title_text(text=req.fulltext)
    n, code = models.node.add(
        uid=uc.uid,
        title=title,
        text=text,
        type_=req.type,
        from_nid=req.fromNid,
    )
    if code != const.Code.OK:
        return PutNodeResponse(
            code=code.value,
            message=const.get_msg_by_code(code, uc.language),
            requestId=req.requestId,
            node=None,
        )
    return PutNodeResponse(
        code=code.value,
        message=const.get_msg_by_code(code, uc.language),
        requestId=req.requestId,
        node=__get_node_data(n),
    )


def __get_node_data(n: models.tps.Node) -> NodeData:
    from_nodes: typing.List[NodeData.LinkedNode] = []
    to_nodes: typing.List[NodeData.LinkedNode] = []
    for nodes, key in zip([from_nodes, to_nodes], ["fromNodes", "toNodes"]):
        for _n in n[key]:
            nodes.append(
                NodeData.LinkedNode(
                    id=_n["id"],
                    title=_n["title"],
                    text=_n["text"],
                    snippet=_n["snippet"],
                    type=_n["type"],
                    disabled=_n["disabled"],
                    createdAt=_n["_id"].generation_time,
                    modifiedAt=_n["modifiedAt"],
                )
            )
    return NodeData(
        id=n["id"],
        title=n["title"],
        text=n["text"],
        type=n["type"],
        disabled=n["disabled"],
        createdAt=datetime2str(n["_id"].generation_time),
        modifiedAt=datetime2str(n["modifiedAt"]),
        fromNodes=from_nodes,
        toNodes=to_nodes,
    )


def get_node_resp(
        uc: UidCode,
        req_id: str,
        nid: str,
) -> GetNodeResponse:
    n, code = models.node.get(uid=uc.uid, nid=nid)
    if code != const.Code.OK:
        return GetNodeResponse(
            requestId=req_id,
            code=code.value,
            message=const.get_msg_by_code(code, uc.language),
            node=None,
        )
    return GetNodeResponse(
        requestId=req_id,
        code=code.value,
        message=const.get_msg_by_code(code, uc.language),
        node=__get_node_data(n),
    )


def update_resp(
        uc: UidCode,
        req: UpdateNodeRequest,
) -> GetNodeResponse:
    if uc.code != const.Code.OK:
        return GetNodeResponse(
            code=uc.code.value,
            message=const.get_msg_by_code(uc.code, uc.language),
            requestId=req.requestId,
            node=None
        )
    title, text = __split_title_text(text=req.fulltext)
    n, code = models.node.update(
        uid=uc.uid,
        nid=req.nid,
        title=title,
        text=text,
    )
    return GetNodeResponse(
        code=code.value,
        message=const.get_msg_by_code(code, uc.language),
        requestId=req.requestId,
        node=__get_node_data(n),
    )


def parse_content_resp(
        uc: UidCode,
        req: CursorQueryRequest,
) -> CursorQueryResponse:
    if uc.code != const.Code.OK:
        return CursorQueryResponse(
            code=uc.code.value,
            message=const.get_msg_by_code(uc.code, uc.language),
            requestId=req.requestId,
            result=None
        )
    query, recommended_nodes = models.node.get_cursor_text_recommend(
        uid=uc.uid,
        nid=req.nid,
        cursor_text=req.textBeforeCursor,
    )
    code = const.Code.OK
    return CursorQueryResponse(
        code=code.value,
        message=const.get_msg_by_code(code, uc.language),
        requestId=req.requestId,
        result=CursorQueryResponse.Result(
            nodes=[NodesInfoResponse.NodeInfo(
                id=n["id"],
                title=n["title"],
                snippet=n["snippet"],
                type=n["type"],
                createdAt=datetime2str(n["_id"].generation_time),
                modifiedAt=datetime2str(n["modifiedAt"]),
                ) for n in recommended_nodes
            ],
            query=query,
        )
    )


def delete_resp(
        uc: UidCode,
        req_id: str,
        nid: str,
) -> AcknowledgeResponse:
    if uc.code != const.Code.OK:
        return AcknowledgeResponse(
            code=uc.code.value,
            message=const.get_msg_by_code(uc.code, uc.language),
            requestId=req_id,
        )
    code = models.node.delete(uid=uc.uid, nid=nid)
    return AcknowledgeResponse(
        code=code.value,
        message=const.get_msg_by_code(code, uc.language),
        requestId=req_id,
    )


def user_node_search_resp(
        uc: UidCode,
        req: SearchUserNodesRequest,
) -> NodesInfoResponse:
    if uc.code != const.Code.OK:
        return NodesInfoResponse(
            code=uc.code.value,
            message=const.get_msg_by_code(uc.code, uc.language),
            requestId=req.requestId,
            nodes=[],
        )
    nodes = models.node.search_user_node(
        uid=uc.uid,
        query=req.query,
        sort_key=req.sortKey,
        sort_order=req.sortOrder,
        page=req.page,
        page_size=req.pageSize,
        nid_exclude=req.nidExclude,
    )
    code = const.Code.OK
    return NodesInfoResponse(
        code=code.value,
        message=const.get_msg_by_code(code, uc.language),
        requestId=req.requestId,
        nodes=[NodesInfoResponse.NodeInfo(
            id=n["id"],
            title=n["title"],
            snippet=n["snippet"],
            type=n["type"],
            createdAt=datetime2str(n["_id"].generation_time),
            modifiedAt=datetime2str(n["modifiedAt"]),
        ) for n in nodes],
    )


def put_cursor_search_selected_node_resp(
        uc: UidCode,
        req: CursorSearchSelectRequest
) -> AcknowledgeResponse:
    if uc.code != const.Code.OK:
        return AcknowledgeResponse(
            code=uc.code.value,
            message=const.get_msg_by_code(uc.code, uc.language),
            requestId=req.requestId,
        )
    code = models.node.cursor_node_selected(uid=uc.uid, nid=req.nid, to_nid=req.toNid)
    return AcknowledgeResponse(
        code=code.value,
        message=const.get_msg_by_code(code, uc.language),
        requestId=req.requestId,
    )
