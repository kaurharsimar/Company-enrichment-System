import asyncio

jobs = {}
lock = asyncio.Lock()
BATCH_SIZE = 100
semaphore = asyncio.Semaphore(5)
