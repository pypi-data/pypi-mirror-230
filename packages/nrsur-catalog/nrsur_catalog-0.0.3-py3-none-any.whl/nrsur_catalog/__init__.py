import logging

from .catalog import Catalog
from .nrsur_result import NRsurResult
from .style import set_style

__version__ = "0.0.3"
__website__ = "https://sxs-collaboration.github.io/"
__uri__ = "https://github.com/sxs-collaboration/nrsur_catalog"
__author__ = "NRSurrogate Catalog Team"
__email__ = "tousifislam24@gmail.com"
__license__ = "MIT"
__description__ = "GW event posteriors obtained using numerical relativity surrogate models"
__copyright__ = "Copyright 2023 NRSurrogate Catalog Team"
__contributors__ = "https://github.com/sxs-collaboration/nrsur_catalog/graphs/contributors"

logging.getLogger("bilby").setLevel(logging.ERROR)
set_style()
