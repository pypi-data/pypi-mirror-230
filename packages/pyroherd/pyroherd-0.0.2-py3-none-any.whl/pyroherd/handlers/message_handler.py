from typing import Callable

from .handler import Handler


class MessageHandler(Handler):
    """The Message handler class. Used to handle new messages.
    It is intended to be used with :meth:`~pyroherd.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyroherd.Client.on_message` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new Message arrives. It takes *(client, message)*
            as positional arguments (look at the section below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of messages to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyroherd.Client`):
            The Client itself, useful when you want to call other API methods inside the message handler.

        message (:obj:`~pyroherd.types.Message`):
            The received message.
    """

    def __init__(self, callback: Callable, filters=None):
        super().__init__(callback, filters)
