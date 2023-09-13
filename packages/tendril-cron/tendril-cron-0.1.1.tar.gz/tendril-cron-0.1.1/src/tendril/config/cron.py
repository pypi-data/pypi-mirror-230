# Copyright (C) 2019 Chintalagiri Shashank
#
# This file is part of Tendril.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Cron Configuration Options
==========================
"""


from tendril.utils.config import ConfigOption
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = ['tendril.config.core']

config_elements_cron = [
    ConfigOption(
        'CRON_ENABLED',
        "False",
        "Whether to enable Cron. This only controls whether "
        "tendril will attempt to locate and install cron jobs. "
        "Note that if a file containing a cron job is imported "
        "by other code, and if the asyncio reactor is running, "
        "then that cron job will probably run irrespective of "
        "this setting."
    ),
    ConfigOption(
        'CRON_PREFIXES',
        "[]",
        "List of package namespaces other than "
        "'tendril.cron.jobs' to search for cron jobs."
    )
]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    manager.load_elements(config_elements_cron,
                          doc="Tendril Cron Configuration")
