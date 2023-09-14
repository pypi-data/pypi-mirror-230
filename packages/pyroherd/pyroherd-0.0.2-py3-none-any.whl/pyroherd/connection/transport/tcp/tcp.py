import asyncio
import ipaddress
import logging
import socket
import time

try:
    import socks
except ImportError as e:
    e.msg = (
        "PySocks is missing and Pyroherd can't run without. "
        "Please install it using \"pip3 install pysocks\"."
    )

    raise e

log = logging.getLogger(__name__)


class TCP:
    TIMEOUT = 10

    def __init__(self, ipv6: bool, proxy: dict):
        self.socket = None

        self.reader = None  # type: asyncio.StreamReader
        self.writer = None  # type: asyncio.StreamWriter

        self.lock = asyncio.Lock()
        self.loop = asyncio.get_event_loop()

        if proxy:
            hostname = proxy.get("hostname")

            try:
                ip_address = ipaddress.ip_address(hostname)
            except ValueError:
                self.socket = socks.socksocket(socket.AF_INET)
            else:
                if isinstance(ip_address, ipaddress.IPv6Address):
                    self.socket = socks.socksocket(socket.AF_INET6)
                else:
                    self.socket = socks.socksocket(socket.AF_INET)

            self.socket.set_proxy(
                proxy_type=getattr(socks, proxy.get("scheme").upper()),
                addr=hostname,
                port=proxy.get("port", None),
                username=proxy.get("username", None),
                password=proxy.get("password", None)
            )

            log.info(f"Using proxy {hostname}")
        else:
            self.socket = socks.socksocket(
                socket.AF_INET6 if ipv6
                else socket.AF_INET
            )

        self.socket.settimeout(TCP.TIMEOUT)

    async def connect(self, address: tuple):
        self.socket.connect(address)
        self.reader, self.writer = await asyncio.open_connection(sock=self.socket)

    def close(self):
        try:
            self.writer.close()
        except AttributeError:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            finally:
                # A tiny sleep placed here helps avoiding .recv(n) hanging until the timeout.
                # This is a workaround that seems to fix the occasional delayed stop of a client.
                time.sleep(0.001)
                self.socket.close()

    async def send(self, data: bytes):
        async with self.lock:
            self.writer.write(data)
            await self.writer.drain()

    async def recv(self, length: int = 0):
        data = b""

        while len(data) < length:
            try:
                chunk = await asyncio.wait_for(
                    self.reader.read(length - len(data)),
                    TCP.TIMEOUT
                )
            except (OSError, asyncio.TimeoutError):
                return None
            else:
                if chunk:
                    data += chunk
                else:
                    return None

        return data
