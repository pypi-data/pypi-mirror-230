import asyncio
from asyncio import QueueEmpty

from contact_magic.conf.settings import SETTINGS
from contact_magic.logger import logger


async def do_bulk(ops: list, max_workers: int = SETTINGS.MAX_WORKERS):
    """
    Bulk operation
    This function can be used to run bulk operations
    using a limited number of concurrent requests.
    """
    results = [None for _ in range(len(ops))]

    queue = asyncio.Queue()

    for job in enumerate(ops):
        await queue.put(job)

    workers = [_worker(queue, results) for _ in range(max_workers)]

    await asyncio.gather(*workers)

    return results


async def _worker(queue: asyncio.Queue, results: list):
    while True:
        try:
            index, op = queue.get_nowait()
        except QueueEmpty:
            break

        try:
            response = await op[0](**op[1])
            results[index] = response
        except Exception as e:
            logger.error(
                "processing_row",
                row_number=op[1]["row"].index,
                status="ERROR",
                message=e,
            )
            results[index] = op[1]["row"]
        queue.task_done()
