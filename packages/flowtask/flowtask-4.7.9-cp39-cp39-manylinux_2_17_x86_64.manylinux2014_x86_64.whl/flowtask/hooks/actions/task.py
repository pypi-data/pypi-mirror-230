from .abstract import AbstractAction


class Task(AbstractAction):
    """Task.

    Calling an FlowTask Task.
    """
    async def close(self):
        pass

    async def open(self):
        pass

    async def run(self):
        pass
