from .abstract import AbstractEvent


class Notify(AbstractEvent):
    async def __call__(self, *args, **kwargs):
        pass
