from typing import Callable

from .handler import Handler


class CallbackQueryHandler(Handler):
    """The CallbackQuery handler class. Used to handle callback queries coming from inline buttons.
    It is intended to be used with :meth:`~pyroherd.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyroherd.Client.on_callback_query` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new CallbackQuery arrives. It takes *(client, callback_query)*
            as positional arguments (look at the section below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of callback queries to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyroherd.Client`):
            The Client itself, useful when you want to call other API methods inside the message handler.

        callback_query (:obj:`~pyroherd.types.CallbackQuery`):
            The received callback query.
    """

    def __init__(self, callback: Callable, filters=None):
        super().__init__(callback, filters)
