from typing import Union

import pyroherd
from pyroherd import raw


class SendInlineBotResult:
    async def send_inline_bot_result(
        self: "pyroherd.Client",
        chat_id: Union[int, str],
        query_id: int,
        result_id: str,
        disable_notification: bool = None,
        reply_to_message_id: int = None
    ):
        """Send an inline bot result.
        Bot results can be retrieved using :meth:`~pyroherd.Client.get_inline_bot_results`

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            query_id (``int``):
                Unique identifier for the answered query.

            result_id (``str``):
                Unique identifier for the result that was chosen.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            reply_to_message_id (``bool``, *optional*):
                If the message is a reply, ID of the original message.

        Returns:
            :obj:`~pyroherd.types.Message`: On success, the sent inline result message is returned.

        Example:
            .. code-block:: python

                await app.send_inline_bot_result(chat_id, query_id, result_id)
        """
        return await self.invoke(
            raw.functions.messages.SendInlineBotResult(
                peer=await self.resolve_peer(chat_id),
                query_id=query_id,
                id=result_id,
                random_id=self.rnd_id(),
                silent=disable_notification or None,
                reply_to_msg_id=reply_to_message_id
            )
        )
