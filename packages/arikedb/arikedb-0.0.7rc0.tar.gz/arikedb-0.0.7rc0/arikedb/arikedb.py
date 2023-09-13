import json
import socket
import ssl
from json.decoder import JSONDecodeError
from threading import Thread
from typing import Optional, List, Iterable, Callable

from arikedb.command import Command
from arikedb.events import TagEvent
from arikedb.exceptions import ArikedbClientError
from arikedb.tool_box.socket_tools import socket_send, socket_recv


class ArikedbClient:

    def __init__(self, host: str = "localhost", port: int = 6923,
                 cert_file: Optional[str] = None):
        """RTDB Client constructor"""
        self._host = host
        self._port = port
        self._cert = cert_file
        self._socket = None
        self._ssl_ctx = None
        self._subscribed = None
        self._reading_sub = False

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if self._cert:
            self._ssl_ctx = ssl.create_default_context(
                ssl.Purpose.SERVER_AUTH
            )
            self._ssl_ctx.load_verify_locations(cafile=self._cert)
            self._socket = self._ssl_ctx.wrap_socket(
                self._socket, server_hostname=self._host
            )

        self._socket.connect((self._host, self._port))

    def send_command(self, cmd: str) -> dict:
        socket_send(self._socket, cmd)
        x = socket_recv(self._socket)
        response = json.loads(x)
        return response

    def disconnect(self) -> dict:
        self.unsubscribe()
        return self.send_command("EXIT")

    def list_databases(self) -> List[str]:
        resp = self.send_command("SHOW databases")
        status = resp.get("status")
        if status == 0:
            return resp.get("databases")
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error listing databases. "
                                     f"Err code {status}. {msg}")

    def list_roles(self) -> List[str]:
        resp = self.send_command("SHOW roles")
        status = resp.get("status")
        if status == 0:
            return resp.get("roles")
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error listing roles. "
                                     f"Err code {status}. {msg}")

    def list_users(self) -> List[str]:
        resp = self.send_command("SHOW users")
        status = resp.get("status")
        if status == 0:
            return resp.get("users")
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error listing users. "
                                     f"Err code {status}. {msg}")

    def use(self, database: str) -> int:
        resp = self.send_command(f"USE_DATABASE {database}")
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error using database. "
                                     f"Err code {status}. {msg}")

    def set(self, tags_data: dict, meta: dict = None,
            timestamp: float = None) -> int:
        cmd = "SET"
        for k, v in tags_data.items():
            cmd += f' "{k}" "{v}"'
        if meta:
            cmd += " META"
            for k, v in meta.items():
                cmd += f' "{k}" "{v}"'
        if timestamp:
            cmd += f" TS {timestamp}"
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error setting tags. "
                                     f"Err code {status}. {msg}")

    def set_event(self, tags: List[str], event: TagEvent,
                  threshold: Optional[float] = None,
                  min_: Optional[float] = None, max_: Optional[float] = None,
                  rate_threshold: Optional[float] = None) -> int:
        cmd = "SET_EVENT"
        for tag in tags:
            cmd += f' "{tag}"'
        cmd += f" EVENT {event.value}"
        if isinstance(threshold, (float, int)):
            cmd += f" THRESHOLD {threshold}"
        if isinstance(min_, (float, int)):
            cmd += f" MIN {min_}"
        if isinstance(max_, (float, int)):
            cmd += f" MAX {max_}"
        if isinstance(rate_threshold, (float, int)):
            cmd += f" RATE_THRESHOLD {rate_threshold}"
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error setting tags event. "
                                     f"Err code {status}. {msg}")

    def get(self, tags: List[str], epoch: str = None):
        cmd = "GET "
        for tag in tags:
            cmd += f' "{tag}"'
        if isinstance(epoch, str):
            cmd += f" EPOCH {epoch}"
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return resp.get("values")
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error getting tag values. "
                                     f"Err code {status}. {msg}")

    def pget(self, patterns: List[str], epoch: str = None):
        cmd = "PGET "
        for pat in patterns:
            cmd += f' "{pat}"'
        if isinstance(epoch, str):
            cmd += f" EPOCH {epoch}"
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return resp.get("values")
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error getting tag values. "
                                     f"Err code {status}. {msg}")

    def subscribe(self, tags: List[str], callback: Callable,
                  epoch: str = None, event: Optional[TagEvent] = None,
                  threshold: Optional[float] = None,
                  min_: Optional[float] = None, max_: Optional[float] = None,
                  rate_threshold: Optional[float] = None) -> int:
        cmd = "SUBSCRIBE "
        for tag in tags:
            cmd += f' "{tag}"'
        if isinstance(epoch, str):
            cmd += f" EPOCH {epoch}"
        if isinstance(event, TagEvent):
            cmd += f" EVENT {event.value}"
        if isinstance(threshold, (float, int)):
            cmd += f" THRESHOLD {threshold}"
        if isinstance(min_, (float, int)):
            cmd += f" MIN {min_}"
        if isinstance(max_, (float, int)):
            cmd += f" MAX {max_}"
        if isinstance(rate_threshold, (float, int)):
            cmd += f" RATE_THRESHOLD {rate_threshold}"
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            self._subscribed = resp.get("sub_id")

            def wrapper():
                for data in self._iter_subscription():
                    for tag_data in data:
                        callback(*tag_data)

            Thread(target=wrapper, daemon=True).start()
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error subscribing to tags. "
                                     f"Err code {status}. {msg}")

    def psubscribe(self, patterns: List[str], callback: Callable,
                   epoch: str = None, event: Optional[TagEvent] = None,
                   threshold: Optional[float] = None,
                   min_: Optional[float] = None, max_: Optional[float] = None,
                   rate_threshold: Optional[float] = None) -> int:
        cmd = "PSUBSCRIBE "
        for pattern in patterns:
            cmd += f' "{pattern}"'
        if isinstance(epoch, str):
            cmd += f" EPOCH {epoch}"
        if isinstance(event, TagEvent):
            cmd += f" EVENT {event.value}"
        if isinstance(threshold, (float, int)):
            cmd += f" THRESHOLD {threshold}"
        if isinstance(min_, (float, int)):
            cmd += f" MIN {min_}"
        if isinstance(max_, (float, int)):
            cmd += f" MAX {max_}"
        if isinstance(rate_threshold, (float, int)):
            cmd += f" RATE_THRESHOLD {rate_threshold}"
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            self._subscribed = resp.get("sub_id")

            def wrapper():
                for data in self._iter_subscription():
                    for tag_data in data:
                        callback(*tag_data)

            Thread(target=wrapper, daemon=True).start()
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error psubscribing to tags. "
                                     f"Err code {status}. {msg}")

    def unsubscribe(self) -> int:
        if self._subscribed:
            cmd = f"UNSUBSCRIBE {self._subscribed}"
            self._send_unack_command(cmd)
            if not self._reading_sub:
                self._subscribed = False
            return 0

    def add_database(self, db_name: str) -> int:
        cmd = f"ADD_DATABASE {db_name}"
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error creating database. "
                                     f"Err code {status}. {msg}")

    def del_database(self, db_name: str) -> int:
        cmd = f"DEL_DATABASE {db_name}"
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error deleting database. "
                                     f"Err code {status}. {msg}")

    def auth(self, username: str, password: str):
        cmd = f'AUTH "{username}" "{password}"'
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error authenticating. "
                                     f"Err code {status}. {msg}")

    def add_role(self, role_name: str, allowed_commands: List[Command]) -> int:
        cmds = [c.value for c in allowed_commands]
        cmd = f'ADD_ROLE "{role_name}" {" ".join(cmds)}'
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error creating role. "
                                     f"Err code {status}. {msg}")

    def del_role(self, role_name: str) -> int:
        cmd = f'DEL_ROLE "{role_name}"'
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error deleting role. "
                                     f"Err code {status}. {msg}")

    def add_user(self, role_name: str, username: str, password: str) -> int:
        cmd = f'ADD_USER "{role_name}" "{username}" "{password}"'
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error creating user. "
                                     f"Err code {status}. {msg}")

    def del_user(self, username: str) -> int:
        cmd = f'DEL_USER "{username}"'
        resp = self.send_command(cmd)
        status = resp.get("status")
        if status == 0:
            return 0
        else:
            msg = resp.get("msg")
            raise ArikedbClientError(f"Error deleting user. "
                                     f"Err code {status}. {msg}")

    def _send_unack_command(self, cmd: str):
        socket_send(self._socket, cmd)

    def _iter_subscription(self) -> Iterable:
        self._reading_sub = True
        while self._subscribed:
            try:
                response = json.loads(socket_recv(self._socket))
                if response.get("sub_id") == "-1":
                    self._subscribed = False
                if "values" in response:
                    yield response["values"]
            except (JSONDecodeError, TypeError) as err:
                _ = err
        self._reading_sub = False
