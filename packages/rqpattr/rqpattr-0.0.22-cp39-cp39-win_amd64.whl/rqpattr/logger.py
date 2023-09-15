# -*- coding: utf-8 -*-
import os
import logging

logger = logging.getLogger("p_attr")
logger.propagate = False
logger.handlers.clear()
hdl = logging.StreamHandler()
fmt = logging.Formatter("[%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s/%(process)s] %(message)s")
hdl.setFormatter(fmt=fmt)
logger.addHandler(hdl)
logger.setLevel(os.environ.get("p_attr_log_level", "INFO"))
