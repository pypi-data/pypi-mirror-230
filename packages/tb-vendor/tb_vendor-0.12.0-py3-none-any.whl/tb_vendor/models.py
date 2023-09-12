from dataclasses import dataclass
from typing import Any, Optional, Protocol


@dataclass
class TbPagination:
    """Thingsboard pagitation data.

    python-instalation/site-packages/tb_rest_client/models/models_ce/page_data_*.py

    from tb_rest_client.models.models_ce.page_data_device import PageDataDevice  # CE-PE
    """

    data: list  # can't be more specific
    total_pages: int
    total_elements: int
    has_next: bool


@dataclass
class Telemetry(Protocol):
    """Telemetry data used to send to Thingsboard.

    Define only the attributes that will be sent as telemetry.
    So, attributes like id must no be included.

    .. code-block::

        # Has the desired attrs only.

        class MyTelemetry(Telemetry):
            dimmer: float
            light: bool
    """

    ...


@dataclass
class VendorDevice(Protocol):
    """Vendor data Telemetry.

    Define the vendor telemetry data you wish to use.
    It depends on data returned by the vendor and the
    data you wish to include.

    Attributes:
        vendor_id: Use as ID that vendor handle.
            The type of ID can be many types: int, str, UUIDs, etc.

    .. code-block::

        class MyVendorTelemetry(VendorTelemetry):
            vendor_id: str
            dimmer: float
            light: str = 'ON'
    """

    vendor_id: Any
    telemetry: Optional[Telemetry] = None


@dataclass
class TbVirtualDevice:
    """Thingsboard Device defined"""

    # Thingsboard related
    device_id: str  # ID genereated by Thingsboard
    dtype: str  # Equivalent to Device Profile
    name: str  # Name of device
    access_token: Optional[str] = None
    entity_type: str = "DEVICE"
    label: Optional[str] = None

    # Vendor related
    # At this point both are required to identify between
    # Thingsboard Devices and Vendor Devices
    vendor_id: Optional[str] = None
    vendor_device: Optional[VendorDevice] = None
    # telemetry: Optional[Telemetry] = None
