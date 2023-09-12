# Thingsboard vendor integrations

Create a generic package with utilities to integrate Thingsboards and vendors.

## Thingsboard Issues

Thingsboard Python SDK has a client for PE and other for CE.

## Examples

```python
import logging

from tb_vendor.models import TbVirtualDevice
from tb_vendor.mqtt.callbacks import OnMessageHandler
from tb_vendor.mqtt.parsers import RpcParserBase, AttributeParserBase
from tb_vendor.mqtt import clients as tb_clients

logger = logging.getLogger(__name__)

device_access_token = "access-token"
device_id = "0999e290-3c4f-11ee-8ff7-12785784c398"
# Connection settings
mqtt_keepalive = 60
mqtt_host = "broker-mqtt.example.com"
mqtt_port = 1883

# Create implementations

class MyRpcParser(RpcParserBase):
    def parse_message(self, client, topic, payload: dict, userdata: dict):
        logger.debug(f"payload: {payload}")
        # logger.debug(f"userdata: {userdata}")
        if payload["method"] == "getValue":
            self.rpc_response(client, topic, 7)


class MyAttributeParser(AttributeParserBase):
    def parse_message(self, payload: dict) -> None:
        logger.info(f"payload: {payload}")


# Configure MQTT

my_rpc_parser = MyRpcParser()
my_attribute_parser = MyAttributeParser()
on_message_hanlder = OnMessageHandler(my_rpc_parser, my_attribute_parser)
tb_device_handler = tb_clients.TbDeviceMqttHandler()

# Add custom user data (MQTT userdata)
user_data = {
    "vendor_id": "1000",
    "access_token": device_access_token,
    "device_id": device_id,
}
device = TbVirtualDevice(
    device_id=device_id,
    access_token=device_access_token,
    dtype="GENERIC",
    name="Test Device",
)
conn = tb_clients.TbMqttConnection(
    host=mqtt_host, port=mqtt_port, keepalive=mqtt_keepalive
)

conn.configure_client(
    on_message=on_message_hanlder.callback, userdata=user_data, client_id=device_id
)
conn.add_access_token(device_access_token)
client = conn.mqtt_client
conn.connect_blocking()
```

## Breaking changes

- 050: wait_to_login has moved and named login_wait
- 060: move validate_login
