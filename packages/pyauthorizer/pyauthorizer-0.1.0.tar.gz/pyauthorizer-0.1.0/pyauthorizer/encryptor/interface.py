import inspect
import os
import pkgutil
from pathlib import Path

from pyauthorizer.encryptor.base import BaseEncryptor
from pyauthorizer.encryptor.plugin_manager import EncryptorPlugins

# Create a global registry
plugin_store = EncryptorPlugins()

# Register builtin plugins
current_directory = Path(os.path.dirname(os.path.abspath(__file__))).joinpath("builtin")
for _, module_name, _ in pkgutil.iter_modules([str(current_directory)]):
    plugin_store.register(module_name, f"pyauthorizer.encryptor.builtin.{module_name}")


def get_encryptor(target):
    """
    Get an encryptor object based on the target.

    Args:
        target (str): The target for which the encryptor object is needed.

    Returns:
        BaseEncryptor: An instance of a class that is a subclass of BaseEncryptor, or None if no matching encryptor is found.
    """
    # Get the plugin corresponding to the target
    plugin = plugin_store[target]
    for _, obj in inspect.getmembers(plugin):
        # Check if the object is a class and a subclass of BaseEncryptor
        if inspect.isclass(obj) and issubclass(obj, BaseEncryptor) and obj != BaseEncryptor:
            # Return an instance of the class
            return obj()
    return None
