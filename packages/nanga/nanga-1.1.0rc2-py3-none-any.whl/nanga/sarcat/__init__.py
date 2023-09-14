# @copyright  Copyright (c) 2018-2020 Opscidia

import logging

from .models import legacy
from .predictions import Predictor, Predictors

__version__ = '1.1.0.rc2'

logger = logging.getLogger('sarcat')
if not logger.handlers:  # To ensure reload() doesn't add another one
    logger.addHandler(logging.NullHandler())
