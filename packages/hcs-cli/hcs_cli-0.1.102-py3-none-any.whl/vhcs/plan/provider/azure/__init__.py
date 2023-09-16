from ._prepare import prepare

import logging

logging.getLogger("azure.core").setLevel(logging.WARNING)
logging.getLogger("azure.identity").setLevel(logging.WARNING)
