from dataclasses import dataclass
import logging

from .constants import LIB_NAME
from .logging import create_logger


@dataclass
class ExtractResult:
  logger: logging.Logger


def extract_common_kwargs(**kwargs) -> ExtractResult:
  # TODO env log level
  logger = kwargs['logger'] if 'logger' in kwargs else create_logger(LIB_NAME)
  return ExtractResult(logger=logger)
