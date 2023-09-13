

import aiocron
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


# @aiocron.crontab('*/1 * * * *', start=False)
# async def example_func():
#     logger.info("CRON EXEC")
#
#
# example_func.start()
