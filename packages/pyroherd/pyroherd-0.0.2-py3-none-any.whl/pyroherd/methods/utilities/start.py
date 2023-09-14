import logging

import pyroherd
from pyroherd import raw

log = logging.getLogger(__name__)


class Start:
    async def start(
        self: "pyroherd.Client"
    ):
        """Start the client.

        This method connects the client to Telegram and, in case of new sessions, automatically manages the
        authorization process using an interactive prompt.

        Returns:
            :obj:`~pyroherd.Client`: The started client itself.

        Raises:
            ConnectionError: In case you try to start an already started client.

        Example:
            .. code-block:: python

                from pyroherd import Client

                app = Client("my_account")


                async def main():
                    await app.start()
                    ...  # Invoke API methods
                    await app.stop()


                app.run(main())
        """
        is_authorized = await self.connect()

        try:
            if not is_authorized:
                await self.authorize()

            if not await self.storage.is_bot() and self.takeout:
                self.takeout_id = (await self.invoke(raw.functions.account.InitTakeoutSession())).id
                log.warning(f"Takeout session {self.takeout_id} initiated")

            await self.invoke(raw.functions.updates.GetState())
        except (Exception, KeyboardInterrupt):
            await self.disconnect()
            raise
        else:
            await self.initialize()
            return self
