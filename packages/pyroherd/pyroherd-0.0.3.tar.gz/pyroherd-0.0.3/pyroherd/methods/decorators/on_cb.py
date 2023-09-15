from typing import Callable

import pyroherd
from pyroherd.filters import Filter


class OnCallbackQuery:
    def on_cb(
        self=None,
        filters=None,
        group: int = 0
    ) -> Callable:
        """Decorator for handling callback queries.

        This does the same thing as :meth:`~pyroherd.Client.add_handler` using the
        :obj:`~pyroherd.handlers.CallbackQueryHandler`.

        Parameters:
            filters (:obj:`~pyroherd.filters`, *optional*):
                Pass one or more filters to allow only a subset of callback queries to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: Callable) -> Callable:
            if isinstance(self, pyroherd.Client):
                self.add_handler(pyroherd.handlers.CallbackQueryHandler(func, filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append(
                    (
                        pyroherd.handlers.CallbackQueryHandler(func, self),
                        group if filters is None else filters
                    )
                )

            return func

        return decorator
