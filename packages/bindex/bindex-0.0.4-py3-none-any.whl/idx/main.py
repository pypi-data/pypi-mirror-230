import asyncio

from beni import btask

from .tasks import *


def run():
    btask.options.lock = 'idx'
    asyncio.run(btask.main())
