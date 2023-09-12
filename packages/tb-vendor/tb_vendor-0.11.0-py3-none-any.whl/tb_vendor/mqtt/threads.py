from abc import ABC, abstractmethod
import json
import logging
from multiprocessing.connection import Connection
from threading import Thread

from tb_vendor.mqtt import clients
from tb_vendor.mqtt.topics import TELEMETRY_TOPIC

logger = logging.getLogger(__name__)


class ThreadHandlerBase(ABC):
    """Abstract base class for threads.

    Use this class for any thread you need to implement along with Process.

    Attributes:
        child_conn: Multiprocessing Connection child for receiving data.
        tb_mqtt_connection: TbMqttConnection to handler mqtt client.
        default_target_kwargs: Default arguments for (target) Thread(target=self.blocking_exec)

    Args:
        child_conn: Multiprocessing Connection child for receiving data.
        tb_mqtt_connection: TbMqttConnection to handler mqtt client.
    """

    def __init__(
        self,
        child_conn: Connection = None,
        tb_mqtt_connection: clients.TbMqttConnection = None,
    ) -> None:
        self.__child_conn = child_conn
        self.__tb_mqtt_connection = tb_mqtt_connection

    @property
    def child_conn(self) -> Connection:
        if self.__child_conn is None:
            raise ValueError("child_conn is not set")
        return self.__child_conn

    @child_conn.setter
    def child_conn(self, value: Connection) -> None:
        self.__child_conn = value

    @property
    def tb_mqtt_connection(self) -> clients.TbMqttConnection:
        if self.__tb_mqtt_connection is None:
            raise ValueError("tb_mqtt_connection is not set")
        return self.__tb_mqtt_connection

    @tb_mqtt_connection.setter
    def tb_mqtt_connection(self, value: clients.TbMqttConnection) -> None:
        self.__tb_mqtt_connection = value

    @property
    def default_target_kwargs(self) -> dict:
        return {
            "child_conn": self.child_conn,
            "tb_mqtt_connection": self.tb_mqtt_connection,
        }

    def define_thread(
        self,
        name: str = None,
        daemon: bool = False,
        *target_args,
        **target_kwargs,
    ) -> Thread:
        """Help to generate a new Thread.

        Args:
            name: Thread name
            daemon: Thread daemon
            *target_args: Thread args
            **target_kwargs: Thread kwargs

        Returns:
            A new Thread.
        """
        if "child_conn" in target_kwargs:
            raise ValueError("child_conn is set by default")
        if "tb_mqtt_connection" in target_kwargs:
            raise ValueError("tb_mqtt_connection is set by default")
        target_kwargs.update(self.default_target_kwargs)
        return Thread(
            target=self.blocking_exec,
            name=name,
            args=target_args,
            kwargs=target_kwargs,
            daemon=daemon,
        )

    @abstractmethod
    def get_thread(self, *target_args, **target_kwargs) -> Thread:
        """Implement Callable used in Thread(target=self.get_thread).

        Add *target_args and **target_kwargs according to: "blocking_exec".

        .. code-block:: python

            class MyThreadHandler(ThreadHandlerBase):

                def blocking_exec(self, arg1, arg2, kw1=kw1, kw2=kw2):
                    print('Do nothing')

                def get_thread(self):
                    # if not args and kwargs: return super.get_thread()
                    return self.define_thread(arg1, arg2, kw1=kw1, kw2=kw2)

        Args:
            *target_args: Thread args
            **target_kwargs: Thread kwargs

        Returns:
            A new Thread configured with *target_args and **target_kwargs and
            defaults.
        """
        return self.define_thread()

    @abstractmethod
    def blocking_exec(
        self,
        child_conn: Connection,
        tb_mqtt_connection: clients.TbMqttConnection,
        *target_args,
        **target_kwargs,
    ) -> None:
        """This is the target in Thread. Must be a blocking exectuion function.

        Definition: target=self.blocking_exec `Thread(target=self.blocking_exec, ...)`

        .. code-block:: python

            def blocking_exec(self, child_conn, arg1, arg2, kw1=kw1, kw2=kw2):
                while True:
                    do_nothing(arg1, arg2, kw1=kw1, kw2=kw2)
                    sleep(1)

                # Other blocking exectuion
                # Thread.join()
                # Connection.recv()
                # Process.join()

        Args:
            child_conn: Multiprocessing Connection child for receiving data
                from main process. If no data is required to receive, you can
                ignore this argument.
        """


class MqttListernerRpcThreadHandler(ThreadHandlerBase):
    """Implement a ThreadHandler for Mqtt Listerner RPC."""
    def get_thread(self) -> Thread:
        return super().get_thread()

    def blocking_exec(
        self, child_conn: Connection, tb_mqtt_connection: clients.TbMqttConnection
    ) -> None:
        tb_mqtt_connection.connect_blocking()


class MqttTelemetryThreadHandler(ThreadHandlerBase):
    """Implements ThreadHandler for Telemetry Thread.

    Args:
        topic: Topic for telemetry
        *args: ThreadHandlerBase args
        **kwargs: ThreadHandlerBase kwargs
    """

    def __init__(self, topic: str = TELEMETRY_TOPIC, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.topic = topic

    def get_thread(self) -> Thread:
        return super().define_thread(topic=self.topic)

    def blocking_exec(
        self,
        child_conn: Connection,
        tb_mqtt_connection: clients.TbMqttConnection,
        topic: str,
    ) -> None:
        """Function to be using in Thread. Blocks the execution."""
        mqtt_client = tb_mqtt_connection.mqtt_client
        while True:
            telemetry_data: dict = child_conn.recv()
            # logger.debug('Telemetry data received in process.')
            json_data = json.dumps(telemetry_data)
            mqtt_client.publish(topic, json_data)
