import base64
import hashlib
import random
import string


class VerifierMixin:
    def __init__(self):
        self._code_verifier = None
        self._code_challenge = None

    @property
    def code_verifier(self):
        """랜덤 문자열 생성 후 base64로 인코딩"""
        if self._code_verifier:
            return self._code_verifier
        code_verifier = "".join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(random.randint(43, 128))
        )
        self._code_verifier = base64.urlsafe_b64encode(code_verifier.encode("utf-8"))
        return self._code_verifier

    @code_verifier.setter
    def code_verifier(self, value):
        """code_verifier를 직접 설정"""
        self._code_verifier = base64.urlsafe_b64encode(value.encode("utf-8"))

    @property
    def code_challenge(self):
        """code_verifier를 sha256으로 해싱한 후 base64로 인코딩"""
        if self._code_challenge:
            return self._code_challenge
        code_verifier = self.code_verifier
        code_challenge = hashlib.sha256(code_verifier).digest()
        self._code_challenge = (
            base64.urlsafe_b64encode(code_challenge).decode("utf-8").replace("=", "")
        )
        return self._code_challenge
