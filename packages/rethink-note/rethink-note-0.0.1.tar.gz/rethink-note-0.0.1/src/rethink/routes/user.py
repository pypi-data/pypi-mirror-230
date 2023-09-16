from fastapi import Depends, APIRouter
from typing_extensions import Annotated

from rethink.controllers import (
    user as cu,
    auth as ca,
    base as cb,
)
from rethink.routes.utils import measure_time_spend

router = APIRouter(
    prefix="/api",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/login",
    response_model=cu.UserLoginResponse,
)
@measure_time_spend
async def login(
        req: cu.UserLoginRequest
) -> cu.UserLoginResponse:
    return cu.login_resp(req=req)


@router.put(
    "/user",
    response_model=cu.UserLoginResponse,
)
@measure_time_spend
async def register(
        req: cu.UserRegisterRequest
) -> cu.UserLoginResponse:
    return cu.put_resp(req=req)


@router.get(
    path="/user",
    response_model=cu.UserInfoResponse,
)
@measure_time_spend
async def get_user(
        uid_code: Annotated[ca.UidCode, Depends(ca.token2uid)],
        rid: str = "",
) -> cu.UserInfoResponse:
    return cu.get_user_resp(
        req_id=rid, uc=uid_code
    )


@router.post(
    path="/user",
    response_model=cb.AcknowledgeResponse,
)
@measure_time_spend
async def update_user(
        req: cu.UserUpdateRequest,
        uid_code: Annotated[ca.UidCode, Depends(ca.token2uid)]
) -> cb.AcknowledgeResponse:
    return cu.update_user_resp(
        uc=uid_code,
        req=req,
    )
