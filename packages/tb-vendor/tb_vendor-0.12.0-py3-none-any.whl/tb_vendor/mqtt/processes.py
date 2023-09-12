import logging
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from threading import Thread
from typing import List, TypedDict

from tb_vendor.mqtt.threads import ThreadHandlerBase
from tb_vendor.mqtt.clients import TbMqttConnection

logger = logging.getLogger(__name__)


# import signal
# def close_mqtt_connection_signal_handler(signum: int, frame) -> None:
#     logger.debug("Do noting in signal_handler")
#     # mqtt_handler = clients.TbDeviceMqttHandler()
#     # mqtt_handler.disconnect(tb_mqtt_connection.mqtt_client)
#     return


class ConnectionTypedDict(TypedDict):
    """Represents a dict with Connections from Pipe()."""

    parent_conn: Connection
    child_conn: Connection


class ProcessConnTypedDict(TypedDict):
    """Store the Process and the Connection.

    Use device_id to identify the process which to send data to."""

    process: Process
    conn_dict: ConnectionTypedDict
    device_id: str


def worker_mqtt_connection(threads: List[Thread]) -> None:
    """Worker Process. Designed to be used in Process.

    Start a new process for each MQTT connection. This Process will have their
    own Threads.

    IMPORTANT: process is/must be blocking exectuion: this prvents the threads ends.

    Args:
        threads: List of Thread for this process.
    """
    # signal.signal(signal.SIGTERM, close_mqtt_connection_signal_handler)
    # tb_mqtt_connection.connect_blocking()
    for thread in threads:
        logger.debug(f"Start Thread: {thread.name}")
        thread.start()
    for thread in threads:
        # This ensure wait until all threads are finished
        try:
            thread.join()
        except KeyboardInterrupt:
            pass


def process_join_mqtt_clients(mqtt_connection_processes: List[Process]) -> None:
    """Use .join() to join all the processes.

    This will wait for all the processes to finish.

    Args:
        mqtt_connection_processes: List of processes
    """
    for p in mqtt_connection_processes:
        logger.debug(f"Joining process name={p.name}")
        p.join()


def stop_process_for_mqtt_clients(mqtt_connection_processes: List[Process]) -> None:
    """Force to stop all the processes.

    Args:
        mqtt_connection_processes: List of process of mqtt_connection
    """
    for p in mqtt_connection_processes:
        p.terminate()
        p.join()


def create_process_for_mqtt_clients(
    tb_mqtt_connections: List[TbMqttConnection],
    thread_handlers: List[ThreadHandlerBase],
) -> List[ProcessConnTypedDict]:
    """Create a proccess for each MQTT connection.

    Args:
        tb_mqtt_connections: List of MQTT connections.
        thread_handlers: List of ThreadHandler to get the threads.
    """
    mqtt_connection_processes: List[ProcessConnTypedDict] = []
    len_conn = len(tb_mqtt_connections)
    logger.debug(f"Creating processes for {len_conn} MQTT clients")
    if len_conn == 0:
        raise ValueError("No process to create if no MQTT clients")
    #
    for n, tb_mqtt_connection in enumerate(tb_mqtt_connections, 1):
        logger.debug(f"{n}/{len_conn} Define new process with threads")
        parent_conn, child_conn = Pipe()
        conn_dict: ConnectionTypedDict = {
            "parent_conn": parent_conn,
            "child_conn": child_conn,
        }
        # Add data thread_handler
        for thread_handler in thread_handlers:
            thread_handler.tb_mqtt_connection = tb_mqtt_connection
            thread_handler.child_conn = child_conn

        # Generate threads. Every Process will have len(threads)
        threads = [thread_handler.get_thread() for thread_handler in thread_handlers]

        # Define the process
        p = Process(
            target=worker_mqtt_connection,
            args=(threads,),
        )
        mqtt_connection_processes.append(
            {
                "process": p,
                "conn_dict": conn_dict,
                "device_id": tb_mqtt_connection.client_id,
            }
        )
        logger.debug(f'Start process: {p.name}')
        p.start()
    return mqtt_connection_processes


# def start_process_for_mqtt_clients(process_list: List[Process]):
#     for p in process_list:
#         p.start()
