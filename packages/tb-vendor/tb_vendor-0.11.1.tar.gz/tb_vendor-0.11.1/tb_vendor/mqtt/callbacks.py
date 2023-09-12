import logging
import json
from typing import Callable

import paho.mqtt.client as mqtt

from tb_vendor.mqtt import topics
from tb_vendor.mqtt import parsers

logger = logging.getLogger(__name__)

OnConnectCallable = Callable[[mqtt.Client, dict, dict, int], None]
OnDisconnectCallable = Callable[[mqtt.Client, dict, int], None]
OnMessageCallable = Callable[[mqtt.Client, dict, mqtt.MQTTMessage], None]
OnPublishCallable = Callable[[mqtt.Client, dict, int], None]


def callback_on_connect(
    client: mqtt.Client, userdata: dict, flags: dict, rc: int
) -> None:
    """Callback used to handle connection to ThingsBoard."""
    if rc not in topics.RESULT_CODES:
        logger.warning(f"Unknown result code: rc={rc}")

    """Subscribe to topics."""
    if rc == 0:
        logger.info("Client Connected to ThingsBoard")
        client.subscribe(f"{topics.RPC_REQUEST_TOPIC}+")
        client.subscribe(topics.ATTRIBUTES_TOPIC)
        client.subscribe(f"{topics.ATTRIBUTES_TOPIC_RESPONSE}+")
        client.subscribe(topics.RPC_RESPONSE_TOPIC + "+")
    else:
        logger.info(f"Client Cannot connect to ThingsBoard, rc={rc}")


def callback_on_disconnect(client: mqtt.Client, userdata: dict, rc: int) -> None:
    """Callback used to handle disconnection from ThingsBoard."""
    if rc in topics.RESULT_CODES:
        logger.info(f"Client Disconnected result: {topics.RESULT_CODES[rc]}")
    else:
        logger.warning(f"Client Disconnected. Unknown result code: rc={rc}")


class OnMessageHandler:
    """Class to handle incoming messages

    use method callback for required signature:

    .. code-block::

        on_message(client, userdata, msg)
    """

    def __init__(
        self,
        rpc_parser: parsers.RpcParserBase = None,
        attribute_parser: parsers.AttributeParserBase = None,
    ) -> None:
        self.rpc_parser = rpc_parser
        self.attribute_parser = attribute_parser

    def callback(
        self,
        client: mqtt.Client,
        userdata: dict,
        msg: mqtt.MQTTMessage,
    ):
        """Callback used to handle incoming messages:

        on_message -> instance.callback

        Parse and execute received messages.

        Value examples:
        - msg.topic: v1/devices/me/rpc/request/39
        - msg.payload: {'method': 'getVol', 'params': {'x': 1, 'y': 2}}
        """
        payload = json.loads(msg.payload)

        # Detect topic
        if msg.topic.startswith(topics.RPC_REQUEST_TOPIC):
            logger.debug(f"RPC request topic: {msg.topic}")
            if self.rpc_parser:
                self.rpc_parser.parse(client, msg.topic, payload, userdata)
        elif msg.topic.startswith(topics.ATTRIBUTES_TOPIC):
            logger.debug(f"Attribute update topic: {msg.topic}")
            if self.attribute_parser:
                self.attribute_parser.parse(payload, userdata)
        else:
            logger.debug(f"Unknown topic (nothing to do): {msg.topic}")
