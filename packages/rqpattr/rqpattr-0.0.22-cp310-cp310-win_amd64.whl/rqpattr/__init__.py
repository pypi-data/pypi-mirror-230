from .api import performance_attribute

__all__ = ["performance_attribute"]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
