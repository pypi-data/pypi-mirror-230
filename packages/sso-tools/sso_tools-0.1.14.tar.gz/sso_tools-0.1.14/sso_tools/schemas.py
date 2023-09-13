import enum


class GrantType(enum.StrEnum):
    """인증 방식"""

    CLIENT_CREDENTIALS = "client_credentials"
    AUTHORIZATION_CODE = "authorization_code"


class Token:
    """토큰 정보"""

    def __init__(
        self,
        access_token,
        expires_in,
        token_type,
        scope,
        refresh_token=None,
        id_token=None,
    ):
        # 토큰 정보
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.token_type = token_type
        self.scope = scope
        self.id_token = id_token


class Resource:
    """리소스"""

    def __init__(self, sub, username=None, email=None):
        self.sub = sub
        # 사용자 정보
        self.username = username
        self.email = email
