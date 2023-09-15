from typing import Callable

from .handler import Handler


class EditedMessageHandler(Handler):
    """The EditedMessage handler class. Used to handle edited messages.
     It is intended to be used with :meth:`~pyroherd.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyroherd.Client.on_edited_message` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new edited message arrives. It takes *(client, message)*
            as positional arguments (look at the section below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of messages to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyroherd.Client`):
            The Client itself, useful when you want to call other API methods inside the message handler.

        edited_message (:obj:`~pyroherd.types.Message`):
            The received edited message.
    """

    def __init__(self, callback: Callable, filters=None):
        super().__init__(callback, filters)
