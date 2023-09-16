from fastapi import Depends, APIRouter
from typing_extensions import Annotated

from rethink.controllers import (
    node as cn,
    auth as ca,
    base as cb,
)
from rethink.routes.utils import measure_time_spend

router = APIRouter(
    prefix="/api",
    tags=["node"],
    responses={404: {"description": "Not found"}},
)


@router.put(
    path="/node",
    response_model=cn.PutNodeResponse,
)
@measure_time_spend
async def put_node(
        req: cn.PutNodeRequest,
        uid_code: Annotated[ca.UidCode, Depends(ca.token2uid)]
) -> cn.PutNodeResponse:
    return cn.put_resp(
        uc=uid_code,
        req=req,
    )


@router.get(
    path="/node",
    response_model=cn.GetNodeResponse,
)
@measure_time_spend
async def get_node(
        uid_code: Annotated[ca.UidCode, Depends(ca.token2uid)],
        nid: str,
        rid: str = "",
) -> cn.GetNodeResponse:
    return cn.get_node_resp(
        uc=uid_code,
        req_id=rid,
        nid=nid,
    )


@router.post(
    path="/node",
    response_model=cn.GetNodeResponse,
)
@measure_time_spend
async def update_node(
        req: cn.UpdateNodeRequest,
        uid_code: Annotated[ca.UidCode, Depends(ca.token2uid)]
) -> cn.GetNodeResponse:
    return cn.update_resp(
        uc=uid_code,
        req=req,
    )


@router.post(
    path="/cursorQuery",
    response_model=cn.CursorQueryResponse,
)
@measure_time_spend
async def cursor_query(
        req: cn.CursorQueryRequest,
        uid_code: Annotated[ca.UidCode, Depends(ca.token2uid)]
) -> cn.CursorQueryResponse:
    return cn.parse_content_resp(
        uc=uid_code,
        req=req,
    )


@router.delete(
    path="/node",
    response_model=cb.AcknowledgeResponse,
)
@measure_time_spend
async def delete_node(
        uid_code: Annotated[ca.UidCode, Depends(ca.token2uid)],
        nid: str,
        rid: str = "",
) -> cb.AcknowledgeResponse:
    return cn.delete_resp(
        uc=uid_code,
        req_id=rid,
        nid=nid,
    )


@router.post(
    path="/searchUserNodes",
    response_model=cn.NodesInfoResponse,
)
@measure_time_spend
async def search_user_nodes(
        req: cn.SearchUserNodesRequest,
        uid_code: Annotated[ca.UidCode, Depends(ca.token2uid)]
) -> cn.NodesInfoResponse:
    return cn.user_node_search_resp(
        uc=uid_code,
        req=req,
    )


@router.put(
    path="/cursorSearchSelect",
    response_model=cb.AcknowledgeResponse,
)
@measure_time_spend
async def cursor_search_select(
        req: cn.CursorSearchSelectRequest,
        uid_code: Annotated[ca.UidCode, Depends(ca.token2uid)]
) -> cb.AcknowledgeResponse:
    return cn.put_cursor_search_selected_node_resp(
        uc=uid_code,
        req=req,
    )
