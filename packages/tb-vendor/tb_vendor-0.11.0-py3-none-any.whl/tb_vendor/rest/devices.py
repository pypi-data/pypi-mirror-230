import logging
from time import sleep
from typing import List, Type

from tb_rest_client.rest import ApiException

from tb_vendor.models import TbVirtualDevice
from tb_vendor.tb_utils import tb_paginate
import tb_vendor.rest.models as rest_models
from tb_vendor.rest.login import login_wait

logger = logging.getLogger(__name__)


def request_devices_by_type(
    rest_client: rest_models.RestClientType,
    data_type: str,
    retry_for_timeout: int,
    page_size: int = 100,
) -> List[rest_models.TbDeviceType]:
    """Get all devices by type (DEVICE_PROFILE) from Thingsboard.

    TB method: get_tenant_devices

    Args:
        rest_client: RestClient
        data_type: name of the device profile

    Returns:
        List of Devices as Thingsboard SDK Device

    Raises:
        ApiException
    """
    while True:
        logger.info(f"Get devices of type: {data_type} from TB")
        try:
            devices = tb_paginate(
                rest_client.get_tenant_devices,
                page_size=page_size,
                sort_property="createdTime",
                sort_order="ASC",
                type=data_type,
            )
        except ApiException as e:
            logger.error(f"Error when getting devices: {e}")
            logger.warning(f"Retry in {retry_for_timeout} s")
        else:
            total_devices = len(devices)
            if total_devices > 0:
                break
            logger.warning(f"No devices found, retry in {retry_for_timeout} s")
        sleep(retry_for_timeout)
    return devices


def get_devices_by_type(
    rest_client: rest_models.RestClientType,
    data_type: str,
    retry_for_timeout: int,
    page_size: int = 100,
) -> List[TbVirtualDevice]:
    """Get all devices by type (DEVICE_PROFILE) from Thingsboard.

    Args:
        rest_client: RestClient
        data_type: name of the device profile
        retry_for_timeout: retry timeout
        page_size: page size

    Returns:
        List of Devices as TbVirtualDevice

    Raises:
        ApiException
    """
    tb_virtual_device_list: List[TbVirtualDevice] = []
    tb_devices = request_devices_by_type(
        rest_client,
        data_type,
        retry_for_timeout,
        page_size,
    )
    for tb_device in tb_devices:
        tb_virtual_device = TbVirtualDevice(
            device_id=tb_device.id.id,
            dtype=data_type,
            name=tb_device.name,
        )
        tb_virtual_device_list.append(tb_virtual_device)
    return tb_virtual_device_list


def add_credentials(
    rest_client: rest_models.RestClientType, tb_virtual_devices: List[TbVirtualDevice]
) -> List[TbVirtualDevice]:
    """Add crendentials to device.

    Include info about credentials for each device.

    Args:
        rest_client: RestClient
        tb_virtual_devices: list of devices to be included
    """
    total_devices = len(tb_virtual_devices)
    logger.info(f"Request credentials for {total_devices} devices")
    for n, tb_virtual_device in enumerate(tb_virtual_devices, 1):
        logger.debug(f"Credentials {n}/{total_devices} device {tb_virtual_device.device_id}")
        try:
            credentials = rest_client.get_device_credentials_by_device_id(
                device_id=tb_virtual_device.device_id
            )
        except ApiException as e:
            logger.error(f"Error getting credentials fo {tb_virtual_device.device_id}: {e}")
            continue
        #
        # Add credentials to device
        tb_virtual_device.access_token = credentials.credentials_id
    return tb_virtual_devices


def add_vendor_id(
    rest_client: rest_models.RestClientType,
    tb_virtual_devices: List[TbVirtualDevice],
    EntityIdClass: Type[rest_models.EntityIdType],
) -> List[TbVirtualDevice]:
    """Add vendor id to list of devices.

    Request to Thingsboard to get vendor ID using attributes API then update the
    attributes vendor_id.

    Args:
        rest_client: RestClient
        tb_virtual_devices: list of devices.
    """
    KEY = "vendorId"
    SCOPE = "SHARED_SCOPE"
    ENTITY_TYPE = "DEVICE"
    for tb_virtual_device in tb_virtual_devices:
        device_id = tb_virtual_device.device_id
        entity_id = EntityIdClass(id=device_id, entity_type=ENTITY_TYPE)
        # WARNING: Many api call can be done
        try:
            attributes: List[dict] = rest_client.get_attributes_by_scope(
                entity_id=entity_id,
                scope=SCOPE,
                keys=KEY,
            )
        except ApiException:
            logger.exception(
                f"Error requesting device attributes. device_id {device_id}"
            )
            continue
        if len(attributes) == 0:
            logger.error(
                f"Not Found vendorId. Device {device_id} attritubes: {attributes}"
            )
            continue
        if len(attributes) > 1:
            logger.error(
                f"Found multiple vendorId. Device {device_id} attritubes: {attributes}"
            )
            continue
        if attributes[0]["key"] != KEY:
            logger.error(f"Not found Attribute key: {KEY}. Device {device_id}")
            continue
        vendor_id = attributes[0]["value"]
        logger.debug(f"Found vendorId: {vendor_id} for device {device_id}")
        #
        # Update tb_virtual_device
        tb_virtual_device.vendor_id = vendor_id
    return tb_virtual_devices


def main_device_inventory(
    RestClientKlass: rest_models.RestClientClassType,
    base_url: str,
    username: str,
    password: str,
    data_type: str,
    retry_for_timeout: int = 60,
) -> List[TbVirtualDevice]:
    """Get all devices by type (DEVICE_PROFILE) from Thingsboard.

    TbVirtualDevice include data:
    - device_id
    - access_token
    - name

    TbVirtualDevice not include:
    - vendor_id
    - telemetry

    Args:
        RestClientKlass: Class of RestClientType.
        base_url: URL of Thingsboard.
        username: username for login.
        password: password for login.
        data_type: name of the device profile.
        retry_for_timeout: retry timeout if something go wrong.

    Returns:
        List of devices
    """
    with RestClientKlass(base_url=base_url) as rest_client:
        login_wait(rest_client, username, password, retry_for_timeout)
        device_list = get_devices_by_type(rest_client, data_type, retry_for_timeout)
        devices = add_credentials(rest_client, device_list)

    # Next step: Get vendor ID and relate to each device
    return devices
