import logging
from dataclasses import dataclass

from taren.taren import TaRen
from taren.tarenconfig import TarenConfig


@dataclass
class TarenRuntime:
    config: TarenConfig
    logger: logging.Logger
    runner: TaRen
