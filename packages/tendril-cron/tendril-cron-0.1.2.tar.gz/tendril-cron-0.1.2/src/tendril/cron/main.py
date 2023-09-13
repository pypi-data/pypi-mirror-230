

import asyncio
import importlib
from tendril.config import CRON_ENABLED
from tendril.config import CRON_PREFIXES
from tendril.utils.versions import get_namespace_package_names
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


_default_prefixes = ['tendril.cron.jobs']


def install_jobs(prefixes=CRON_PREFIXES):
    if not CRON_ENABLED:
        return
    prefixes = _default_prefixes + (prefixes or [])
    for prefix in prefixes:
        logger.info("Installing Cron Jobs from '{0}.*'".format(prefix))
        for modname in get_namespace_package_names(prefix):
            logger.debug(f"Trying to install cron jobs from '{modname}'")
            try:
                globals()[modname] = importlib.import_module(modname)
                logger.info("Installed Cron Jobs from {0}".format(modname))
            except ImportError as e:
                logger.debug(e)


def run():
    if not CRON_ENABLED:
        return
    install_jobs()
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    run()
