import asyncio
from typing import List

import pyroherd
from .idle import idle


async def compose(
    clients: List["pyroherd.Client"],
    sequential: bool = False
):
    """Run multiple clients at once.

    This method can be used to run multiple clients at once and can be found directly in the ``pyroherd`` package.

    If you want to run a single client, you can use Client's bound method :meth:`~pyroherd.Client.run`.

    Parameters:
        clients (List of :obj:`~pyroherd.Client`):
            A list of client objects to run.

        sequential (``bool``, *optional*):
            Pass True to run clients sequentially.
            Defaults to False (run clients concurrently)

    Example:
        .. code-block:: python

            import asyncio
            from pyroherd import Client, compose


            async def main():
                apps = [
                    Client("account1"),
                    Client("account2"),
                    Client("account3")
                ]

                ...

                await compose(apps)


            asyncio.run(main())

    """
    if sequential:
        for c in clients:
            await c.start()
    else:
        await asyncio.gather(*[c.start() for c in clients])

    await idle()

    if sequential:
        for c in clients:
            await c.stop()
    else:
        await asyncio.gather(*[c.stop() for c in clients])
