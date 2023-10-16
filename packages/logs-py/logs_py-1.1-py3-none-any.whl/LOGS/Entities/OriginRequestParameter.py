from dataclasses import dataclass
from typing import Optional, Sequence, Union
from uuid import UUID

from LOGS.Entity.EntityRequestParameter import EntityRequestParameter


@dataclass
class OriginRequestParameter(EntityRequestParameter):
    name: Optional[str] = None
    uids: Optional[Sequence[Union[UUID, str]]] = None
