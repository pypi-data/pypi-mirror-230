import logging

import pyroherd
from pyroherd import raw

log = logging.getLogger(__name__)


class Terminate:
    async def terminate(
        self: "pyroherd.Client",
    ):
        """Terminate the client by shutting down workers.

        This method does the opposite of :meth:`~pyroherd.Client.initialize`.
        It will stop the dispatcher and shut down updates and download workers.

        Raises:
            ConnectionError: In case you try to terminate a client that is already terminated.
        """
        if not self.is_initialized:
            raise ConnectionError("Client is already terminated")

        if self.takeout_id:
            await self.invoke(raw.functions.account.FinishTakeoutSession())
            log.warning(f"Takeout session {self.takeout_id} finished")

        await self.storage.save()
        await self.dispatcher.stop()

        for media_session in self.media_sessions.values():
            await media_session.stop()

        self.media_sessions.clear()

        self.is_initialized = False
