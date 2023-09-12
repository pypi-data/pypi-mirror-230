"""KDB.AI Client for Python."""

from importlib.metadata import PackageNotFoundError, version

from .api import KDBAIException, MAX_DATETIME, MIN_DATETIME, Session, Table  # noqa


try:
    __version__ = version('kdbai_client')
except PackageNotFoundError:  # pragma: no cover
    __version__ = 'dev'


__all__ = sorted(['__version__', 'KDBAIException', 'MIN_DATETIME', 'MAX_DATETIME', 'Session', 'Table'])


def __dir__():
    return __all__
