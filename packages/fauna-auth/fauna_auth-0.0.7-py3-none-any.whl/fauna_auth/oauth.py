import json
import logging
import re
from typing import Optional

from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jwcrypto import jwt, jwk

from .public_key import FAUNA_PUBLIC_KEY
from .scopes import authorize_scopes, ScopeAuthorizationError, parse_scopes
from .testing import mocked_auth
from .types import Client, ClientType

USER_ID_PATTERN = re.compile(r"^[a-z0-9]{48}$")

public_key = jwk.JWK.from_pem(FAUNA_PUBLIC_KEY.encode())


class FaunaAuthorizationScheme(OAuth2AuthorizationCodeBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        fauna = request.cookies.get("fauna")
        if fauna is not None:
            return fauna

        return await super().__call__(request)


fauna_auth_scheme = FaunaAuthorizationScheme(authorizationUrl="", tokenUrl="token")


def _parse_token(token: str) -> Optional[Client]:
    try:
        jwt_token = jwt.JWT(
            key=public_key,
            jwt=token,
            check_claims={"exp": None, "iss": "fetch.ai", "sub": None, "iat": None},
        )

        # parse the claims
        claims = json.loads(jwt_token.claims)

        # extract the elements
        subject = str(claims["sub"])
        group = claims.get("grp")

        # ensure that we match the user id pattern
        if USER_ID_PATTERN.match(subject) is None:
            return None

        # capture the scopes, if not present then generate an empty set
        scope = claims.get("scope")
        if scope is not None:
            scopes = parse_scopes(scope)
        else:
            scopes = set()

        # determine client type by the presence of the scopes
        if len(scopes) == 0:
            client_type = ClientType.User
        else:
            client_type = ClientType.Delegate

        return Client(
            client_type=client_type,
            client_id=subject,
            group=group,
            scopes=scopes,
        )

    except (jwt.JWException, ValueError):
        return None


def _is_authorization_mocked(request: Request) -> bool:
    return request.app.state._state.get("authorization_mocked", False)


def get_fauna_client(
    request: Request, token: Optional[str] = Depends(fauna_auth_scheme)
) -> Client:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    if token is None:
        raise credentials_exception

    if _is_authorization_mocked(request):
        logging.warning("Using mocked authorization")
        return mocked_auth(token)

    # normal authorization flow
    client = _parse_token(token)
    if client is None:
        raise credentials_exception

    return client


def get_fauna_user(client: Client = Depends(get_fauna_client)) -> Client:
    if client.client_type != ClientType.User:
        raise HTTPException(status_code=401, detail="Invalid token")
    return client


class GetFaunaClient:
    def __init__(self, requirement_pattern: Optional[str] = None):
        if requirement_pattern is not None and requirement_pattern.endswith(":ro"):
            raise ValueError(
                "Do not specify the read only permission via the requirement. This will be computed automatically by method"
            )

        self._pattern = requirement_pattern

    def __call__(
        self, request: Request, client: Client = Depends(get_fauna_client)
    ) -> Client:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

        # simple path - the authorized client is of user type
        if client.client_type == ClientType.User:
            return client

        # sanity check
        assert client.client_type != ClientType.User

        # no delegated permission pattern - should result in an error
        if self._pattern is None:
            raise credentials_exception

        # sanity check
        assert self._pattern is not None

        # resolve the scope permissions
        try:
            requirement = self._pattern.format(**request.path_params)
            if request.method.lower() == "get":
                requirement += ":ro"

        except KeyError:
            raise credentials_exception

        # validate the scopes that are required
        try:
            authorize_scopes(client.scopes, requirement)
        except ScopeAuthorizationError:
            raise credentials_exception

        # all checks are passed - return the client
        return client
