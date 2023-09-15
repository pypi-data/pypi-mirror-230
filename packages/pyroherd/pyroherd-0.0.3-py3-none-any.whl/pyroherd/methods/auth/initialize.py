import logging

import pyroherd

log = logging.getLogger(__name__)


class Initialize:
    async def initialize(
        self: "pyroherd.Client",
    ):
        """Initialize the client by starting up workers.

        This method will start updates and download workers.
        It will also load plugins and start the internal dispatcher.

        Raises:
            ConnectionError: In case you try to initialize a disconnected client or in case you try to initialize an
                already initialized client.
        """
        if not self.is_connected:
            raise ConnectionError("Can't initialize a disconnected client")

        if self.is_initialized:
            raise ConnectionError("Client is already initialized")

        self.load_plugins()

        await self.dispatcher.start()

        self.me = await self.get_me()

        self.is_initialized = True
