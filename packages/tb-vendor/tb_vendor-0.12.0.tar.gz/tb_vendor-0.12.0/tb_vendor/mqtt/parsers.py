from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
import logging
from typing import Any, Union

from paho.mqtt.client import Client

from tb_vendor.mqtt import topics

logger = logging.getLogger(__name__)

LEN_RPC_REQUEST_TOPIC = len(topics.RPC_REQUEST_TOPIC)

RpcResponseType = Union[bool, int, float, str, dict]


@dataclass
class RpcPayload:
    method: str
    params: dict


class AttributeParserBase(ABC):
    """Base class for attribute parsers."""

    @abstractmethod
    def parse_message(self, payload: dict, userdata: dict) -> Any:
        """Parse received attribute message.

        Args:
            payload (dict): attribute payload.

        Returns:
            Any: attribute value
        """

    def parse(self, payload: dict, userdata: dict) -> None:
        """Parse received attribute message."""
        self.parse_message(payload, userdata)


class RpcParserBase(ABC):
    """Base class for RPC parsers.

    Your vendo integration must implement this class.

    ..code-block::

        class MyRpcParser(RpcParserBase):
            def parse_message(self, client, topic, payload: dict, userdata: dict):
            # Do custom RPC parsing
            ...

        my_rpc_parser = MyRpcParser(...)

    Then you can inject this object to a class that implements it.
    """

    @abstractmethod
    def parse_message(
        self, client: Client, topic: str, payload: dict, userdata: dict
    ) -> RpcResponseType:
        """Parse received RPC message.

        Args:
            client (Client): MQTT client.
            topic (str): topic.
            userdata (dict): user data.
            msg (MQTTMessage): received message.

        Returns:
            Provide a valid response that will be published to the broker. Return
            can be None if no response is required.
        """
        ...
        return  # anything

    def parse(self, client: Client, topic: str, payload: dict, userdata: dict) -> None:
        """Parse received RPC message.

        .parse() invokes rpc_response() when exception is raised. Otherwise
        Developers must implement the response to be published, They can use
        self.rpc_response() to publish the response.
        """
        try:
            self.parse_message(client, topic, payload, userdata)
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            # raise
            response_msg = {"success": False, "error": str(e)}
            request_id = topics.get_request_id(topic)
            self.rpc_response(client, request_id, response_msg)

    def rpc_response(
        self,
        client: Client,
        request_id: str,
        response_msg: Any = None,
    ) -> None:
        """Publish a response to broker when a RPC request is received.

        Args:
            client (Client): MQTT client.
            request_id: Id of the request message.
            response_msg (Any): response message.
        """
        response_topic = f"{topics.RPC_RESPONSE_TOPIC}{request_id}"
        if response_msg is None:
            response_msg = {"success": True, "error": ""}
        logger.debug(f"Publish a response: {response_msg}")
        client.publish(response_topic, json.dumps(response_msg))
