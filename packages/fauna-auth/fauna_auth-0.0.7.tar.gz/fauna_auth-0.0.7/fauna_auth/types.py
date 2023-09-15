from enum import Enum
from typing import Optional, Set

from pydantic import BaseModel


class ClientType(str, Enum):
    User = "user"  # An active user session
    Delegate = "delegate"  # a delegated user session
    App = "app"  # an app session


class Client(BaseModel):
    client_type: ClientType
    client_id: str
    group: Optional[str] = None
    scopes: Set[str]
