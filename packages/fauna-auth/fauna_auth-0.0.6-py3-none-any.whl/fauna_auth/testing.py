from typing import Dict, Optional

from fastapi import HTTPException, status

from .types import Client


class TestingTokenRegister:
    def __init__(self):
        self.tokens: Dict[str, Client] = {}

    def get(self, token: str) -> Optional[Client]:
        return self.tokens.get(token)

    def set(self, token: str, client: Client):
        self.tokens[token] = client

    def delete(self, token: str):
        del self.tokens[token]

    def clear(self):
        self.tokens.clear()


test_token_register = TestingTokenRegister()


def mocked_auth(token: str) -> Client:
    client = test_token_register.get(token)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return client
