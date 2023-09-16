import typing
from dataclasses import dataclass

from rethink import const, models
from . import auth
from .base import AcknowledgeResponse, UidCode, datetime2str


@dataclass
class UserInfoResponse:
    @dataclass
    class User:
        email: str
        nickname: str
        avatar: str
        createdAt: str
        language: str

    code: int
    message: str
    requestId: str
    user: User = None


@dataclass
class UserRegisterRequest:
    email: str
    password: str
    language: str
    requestId: str = ""


@dataclass
class UserLoginRequest:
    email: str
    password: str
    requestId: str = ""


@dataclass
class UserLoginResponse:
    code: int
    message: str
    requestId: typing.Optional[str]
    token: str = ""


@dataclass
class UserUpdateRequest:
    email: str = ""
    nickname: str = ""
    avatar: str = ""
    language: str = ""
    requestId: str = ""


def put_resp(req: UserRegisterRequest) -> UserLoginResponse:
    new_user_id, code = auth.register_user(
        req.email,
        req.password,
        req.language,
    )
    if code != const.Code.OK:
        return UserLoginResponse(
            requestId=req.requestId,
            code=code.value,
            message=const.get_msg_by_code(code, req.language),
            token="",
        )

    token = auth.jwt_encode(
        uid=new_user_id,
        language=req.language,
    )
    return UserLoginResponse(
        requestId=req.requestId,
        code=const.Code.OK.value,
        message=const.get_msg_by_code(const.Code.OK, req.language),
        token=token,
    )


def login_resp(req: UserLoginRequest) -> UserLoginResponse:
    u, code = auth.get_user_by_email(req.email)
    if code != const.Code.OK:
        return UserLoginResponse(
            requestId=req.requestId,
            code=code.value,
            message=const.get_msg_by_code(code, const.Language.EN.value),
            token="",
        )
    if not auth.verify_user(u, req.password):
        code = const.Code.ACCOUNT_OR_PASSWORD_ERROR
        return UserLoginResponse(
            requestId=req.requestId,
            code=code.value,
            message=const.get_msg_by_code(code, u["language"]),
            token="",
        )
    token = auth.jwt_encode(u["id"], u["language"])
    return UserLoginResponse(
        requestId=req.requestId,
        code=code.value,
        message=const.get_msg_by_code(code, u["language"]),
        token=token,
    )


def get_user_resp(
        req_id: str,
        uc: UidCode,
) -> UserInfoResponse:
    if uc.code != const.Code.OK:
        return UserInfoResponse(
            requestId=req_id,
            code=uc.code.value,
            message=const.get_msg_by_code(uc.code, uc.language),
        )
    u, code = models.user.get(uid=uc.uid)
    if code != const.Code.OK:
        return UserInfoResponse(
            requestId=req_id,
            code=code.value,
            message=const.get_msg_by_code(code, uc.language),
        )

    return UserInfoResponse(
        requestId=req_id,
        code=code.value,
        message=const.get_msg_by_code(code, uc.language),
        user=UserInfoResponse.User(
            email=u["email"],
            nickname=u["nickname"],
            avatar=u["avatar"],
            createdAt=datetime2str(u["_id"].generation_time),
            language=u["language"],
        )
    )


def update_user_resp(
        uc: UidCode,
        req: UserUpdateRequest,
) -> AcknowledgeResponse:
    if uc.code != const.Code.OK:
        return AcknowledgeResponse(
            requestId=req.requestId,
            code=uc.code.value,
            message=const.get_msg_by_code(uc.code, uc.language),
        )
    code = models.user.update(
        uid=uc.uid,
        email=req.email,
        nickname=req.nickname,
        avatar=req.avatar,
        language=req.language,
    )
    return AcknowledgeResponse(
        requestId=req.requestId,
        code=code.value,
        message=const.get_msg_by_code(code, uc.language),
    )
