from . import _version
from .yaml import YamlNode, YamlBaseNode, YamlNodeFactory

__version__ = _version.get_versions()['version']


del _version

__all__ = [
    'YamlNode',
    'YamlBaseNode',
    'YamlNodeFactory'
]
