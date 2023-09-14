import pyroherd

from ..object import Object

"""- :obj:`~pyroherd.types.InputLocationMessageContent`
    - :obj:`~pyroherd.types.InputVenueMessageContent`
    - :obj:`~pyroherd.types.InputContactMessageContent`"""


class InputMessageContent(Object):
    """Content of a message to be sent as a result of an inline query.

    pyroherd currently supports the following types:

    - :obj:`~pyroherd.types.InputTextMessageContent`
    """

    def __init__(self):
        super().__init__()

    async def write(self, client: "pyroherd.Client", reply_markup):
        raise NotImplementedError
