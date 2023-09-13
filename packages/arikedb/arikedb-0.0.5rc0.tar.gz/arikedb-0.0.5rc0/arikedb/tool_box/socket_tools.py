
from socket import socket
from typing import Union


def socket_send(socket_: socket, msg: Union[str, bytes, bytearray],
                chunk_size: int = 1024):

    if isinstance(msg, (bytes, bytearray)):
        msg = msg.decode()

    msg_size = len(msg)

    if msg_size > chunk_size:
        prefix = f"{'0' * (12 - len(str(msg_size)))}{msg_size}"
        msg = f"{prefix}{msg}"

    try:
        socket_.sendall(msg.encode())
    except Exception as err:
        _ = err


def socket_recv(socket_: socket, chunk_size: int = 1024) -> str:

    try:
        msg = socket_.recv(chunk_size).decode()
    except Exception as err:
        _ = err
        return ""

    if not msg:
        return msg

    if msg[:12].isdigit():
        msg_size = int(msg[:12])
        msg = msg[12:]

        while len(msg) < msg_size:
            remain = msg_size - len(msg)
            msg = f"{msg}{socket_.recv(min(chunk_size, remain)).decode()}"

    return msg
