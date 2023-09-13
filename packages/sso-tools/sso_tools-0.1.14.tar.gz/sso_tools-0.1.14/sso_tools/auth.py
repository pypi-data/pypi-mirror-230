import base64
import datetime
import os
from urllib.parse import urlencode, unquote

import pytz
import requests

from . import schemas, mixins
from .schemas import GrantType


class OAuth2(mixins.VerifierMixin):
    """OAuth2 인증"""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        server_host=None,
        version=None,
    ):
        super().__init__()
        # 클라이언트 정보
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.server_host = server_host or os.environ.get("MILLIE_SSO_HOST", "")
        self.version = version or "v1"

    def get_authorization_url(
        self,
        scope: str = "read",
        code_verifier: str = None,
        state: str = None,
        next_page: str = None,
    ):
        """인증 URL"""
        if code_verifier:
            # code_verifier를 직접 생성하는 경우
            self.code_verifier = code_verifier
        elif os.getenv("SECRET_KEY"):
            # code_verifier는 SECRET_KEY를 사용
            self.code_verifier = os.getenv("SECRET_KEY")
        else:
            # code_verifier를 여기서 생성하는 경우 state로 전달
            assert not state, "code_verifier는 필수 값입니다.\n직접 전달하거나 SECRET_KEY를 설정해주세요."
            state = self.code_verifier

        # 현재 시간을 base64로 인코딩하여 전달
        now_str = datetime.datetime.now().astimezone(tz=pytz.timezone("Asia/Seoul")).isoformat()
        now_base64 = base64.b64encode(now_str.encode()).decode()
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "code_challenge_method": "S256",
            "code_challenge": self.code_challenge,
            "scope": scope,
            "now": now_base64
        }
        # state는 code_verifier를 사용
        if state:
            params["state"] = state
        # next_page는 로그인 후 이동할 페이지
        if next_page:
            params["next"] = next_page
        url = f"{self.server_host}/{self.version}/oauth2/authorize/?{urlencode(params)}"
        return url

    def _get_client_credentials(self, scope: str):
        """Client Credentials Grant 플로우"""
        url = f"{self.server_host}/{self.version}/oauth2/token/"
        data = {"grant_type": "client_credentials", "scope": scope}
        credential = "{0}:{1}".format(self.client_id, self.client_secret)
        credential = base64.b64encode(credential.encode("utf-8"))
        resp = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache",
                "Authorization": f"Basic {credential.decode('utf-8')}",
            },
        )
        resp.raise_for_status()
        return schemas.Token(**resp.json())

    def _get_authorization_code(self, code: str, code_verifier: str = None):
        """Authorization Code Grant 플로우"""
        code_verifier = (
            unquote(code_verifier) if code_verifier else os.getenv("SECRET_KEY")
        )
        assert code_verifier, "code_verifier를 설정해주세요."
        url = f"{self.server_host}/{self.version}/oauth2/token/"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": unquote(code),
            "redirect_uri": self.redirect_uri,
            "code_verifier": base64.urlsafe_b64encode(code_verifier.encode("utf-8")),
        }
        resp = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache",
            },
        )
        resp.raise_for_status()
        return schemas.Token(**resp.json())

    def get_token(
        self,
        grant_type: GrantType,
        code: str = None,
        code_verifier: str = None,
        scope: str = "openapi",
    ):
        """토큰 발급"""
        if grant_type == GrantType.CLIENT_CREDENTIALS:
            return self._get_client_credentials(scope)
        elif grant_type == GrantType.AUTHORIZATION_CODE:
            return self._get_authorization_code(code, code_verifier)
        raise ValueError(f"Unsupported grant_type: {grant_type}")

    def userinfo(self, access_token: str):
        """사용자 정보"""
        url = f"{self.server_host}/{self.version}/oauth2/userinfo/"
        resp = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return schemas.Resource(**resp.json())

    def refresh_token(self, token: str):
        """토큰 갱신"""
        url = f"{self.server_host}/{self.version}/oauth2/token/"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": token,
        }
        resp = requests.post(
            url,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache",
            },
        )
        resp.raise_for_status()
        return schemas.Token(**resp.json())
