import time
from functools import wraps

from rethink.logger import logger


def measure_time_spend(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        resp = await func(*args, **kwargs)
        t1 = time.perf_counter()
        try:
            req_id = resp.requestId
        except AttributeError:
            req_id = ""
        logger.info(f"reqId='{req_id}' | api='{func.__name__}' | spend={t1 - t0:.4f}s")
        return resp

    return wrapper
