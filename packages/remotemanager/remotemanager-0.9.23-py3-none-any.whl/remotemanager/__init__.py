from .dataset.dataset import Dataset
from .connection.url import URL
from .connection.computers.base import BaseComputer
from .logging.log import Handler
from .storage.remotefunction import RemoteFunction

__all__ = ["Dataset", "URL", "RemoteFunction", "BaseComputer"]  # noqa: F405
__version__ = "0.9.23"

# attach a global Logger to the manager
Logger = Handler()  # noqa: F405


# ipython magic
def load_ipython_extension(ipython):
    from remotemanager.jupyter.magic import RCell

    ipython.register_magics(RCell)
