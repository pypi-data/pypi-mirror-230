import logging

from truera.utils.logging_context.grpc_servicer_context import \
    StdContextFormatter


class TrueraLogger(object):
    """Wrapper for default logger to add a custom formatter and handler.
    Use TrueraLogger(__name__).get_logger() instead of logging.getLogger(__name__)
    """

    def __init__(self, name) -> None:
        self.logger = logging.getLogger(name)
        self._add_logging_formatter()

    def _add_logging_formatter(self) -> None:
        formatter = StdContextFormatter()
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_logger(self) -> logging.Logger:
        return self.logger
