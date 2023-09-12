from typing import Literal, Type, Union

from tb_rest_client import RestClientCE, RestClientPE
from tb_rest_client.models.models_ce.device import Device as DeviceCE
from tb_rest_client.models.models_pe.device import Device as DevicePE
from tb_rest_client.rest_client_ce import (
    EntityId as EntityIdCE,
)
from tb_rest_client.rest_client_pe import (
    EntityId as EntityIdPE,
)

RestClientClassType = Union[Type[RestClientCE], Type[RestClientPE]]
RestClientType = Union[RestClientCE, RestClientPE]
TbDeviceType = Union[DeviceCE, DevicePE]
EntityIdType = Union[EntityIdCE, EntityIdPE]

TbRestVersionLiteral = Literal["PE", "CE"]
