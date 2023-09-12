"""Constants for ThingsBoard MQTT topics or generic MQTT protocol."""

RPC_RESPONSE_TOPIC = "v1/devices/me/rpc/response/"
RPC_REQUEST_TOPIC = "v1/devices/me/rpc/request/"
# In order to publish client-side device attributes to ThingsBoard server node,
# send PUBLISH message to the following topic:
# and In order to subscribe to shared device attribute changes, send SUBSCRIBE message to the following topic:
ATTRIBUTES_TOPIC = "v1/devices/me/attributes"
# Request attribute values from the server
ATTRIBUTES_TOPIC_REQUEST = "v1/devices/me/attributes/request/"
ATTRIBUTES_TOPIC_RESPONSE = "v1/devices/me/attributes/response/"
TELEMETRY_TOPIC = "v1/devices/me/telemetry"
CLAIMING_TOPIC = "v1/devices/me/claim"
PROVISION_TOPIC_REQUEST = "/provision/request"
PROVISION_TOPIC_RESPONSE = "/provision/response"
RESULT_CODES = {
    0: "Successful",
    1: "incorrect protocol version",
    2: "invalid client identifier",
    3: "server unavailable",
    4: "bad username or password",
    5: "not authorised",
}

LEN_RPC_REQUEST_TOPIC = len(RPC_REQUEST_TOPIC)


def validate_request_id_topic(topic: str) -> None:
    """Validate topic starts with RPC_REQUEST_TOPIC.

    Raises:
        ValueError: if invalid topic.
    """
    if not topic.startswith(RPC_REQUEST_TOPIC):
        raise ValueError(f"Invalid topic: {topic}. Must be {RPC_REQUEST_TOPIC}")


def get_request_id(topic: str) -> str:
    """Return the value of the request_id from topic.

    Extract N from v1/devices/me/rpc/request/N

    Args:
        topic: MQTT topic in format v1/devices/me/rpc/request/N

    Returns:
        Number in str for rpc topic request.
    """
    validate_request_id_topic(topic)
    return topic[LEN_RPC_REQUEST_TOPIC:]
