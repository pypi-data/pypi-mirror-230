import logging


def has_level_handler(logger: logging.Logger) -> bool:
  """Check if there is a handler in the logging chain that will handle the
    given logger's :meth:`effective level <~logging.Logger.getEffectiveLevel>`.
    """
  level = logger.getEffectiveLevel()
  current = logger

  while current:
    if any(handler.level <= level for handler in current.handlers):
      return True

    if not current.propagate:
      break

    current = current.parent  # type: ignore

  return False


default_handler = logging.StreamHandler()  # type: ignore
default_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s"))


# TODO cache
def create_logger(name, debug=False) -> logging.Logger:
  logger = logging.getLogger(name)

  if debug and not logger.level:
    logger.setLevel(logging.DEBUG)

  if not has_level_handler(logger):
    logger.addHandler(default_handler)

  return logger
