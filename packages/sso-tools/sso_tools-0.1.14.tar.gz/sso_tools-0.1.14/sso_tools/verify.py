import jwt

from .configs import JWT_ALGORITHMS


def _validate(_token: str, secret_key: str) -> bool:
    """토큰 유효성 검사"""
    if not _token or not secret_key:
        return False
    if not isinstance(_token, str) or not isinstance(secret_key, str):
        return False
    return True


def token(_token: str, secret_key: str) -> dict:
    """토큰 검증"""
    # Bearer 가 포함된 경우 변경
    if "Bearer " in _token and len(_token.split("Bearer ")) == 2:
        _token = _token.split("Bearer ")[1]
    # 유효성 검사
    if not _validate(_token, secret_key):
        raise InvalidTokenFormat("토큰 포멧이 유효하지 않습니다")

    # 토큰 검증
    payload = None
    try:
        payload = jwt.decode(_token, secret_key, algorithms=[JWT_ALGORITHMS])
    except jwt.PyJWTError as e:
        raise InvalidToken(f"토큰이 정상적이지 않습니다\n- 오류 내용 : {e}")

    # 토큰이 존재하지 않음
    if not payload or type(payload) is not dict:
        raise InvalidToken("토큰이 정상적이지 않습니다")
    return payload


class VerifyException(Exception):
    """토큰 검증 오류"""

    pass


class InvalidTokenFormat(VerifyException):
    """토큰 포멧이 유효하지 않음"""

    pass


class InvalidToken(VerifyException):
    """토큰이 정상적이지 않음"""

    pass
