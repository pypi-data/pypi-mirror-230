import pyroherd


class Restart:
    async def restart(
        self: "pyroherd.Client",
        block: bool = True
    ):
        """Restart the Client.

        This method will first call :meth:`~pyroherd.Client.stop` and then :meth:`~pyroherd.Client.start` in a row in
        order to restart a client using a single method.

        Parameters:
            block (``bool``, *optional*):
                Blocks the code execution until the client has been restarted. It is useful with ``block=False`` in case
                you want to restart the own client within an handler in order not to cause a deadlock.
                Defaults to True.

        Returns:
            :obj:`~pyroherd.Client`: The restarted client itself.

        Raises:
            ConnectionError: In case you try to restart a stopped Client.

        Example:
            .. code-block:: python

                from pyroherd import Client

                app = Client("my_account")


                async def main():
                    await app.start()
                    ...  # Invoke API methods
                    await app.restart()
                    ...  # Invoke other API methods
                    await app.stop()


                app.run(main())
        """

        async def do_it():
            await self.stop()
            await self.start()

        if block:
            await do_it()
        else:
            self.loop.create_task(do_it())

        return self
