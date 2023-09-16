from .swift import SwiftObject, SwiftContainer, \
    SwiftService, SwiftNodeFactory, SwiftAuth
from . import _version

__version__ = _version.get_versions()['version']

__all__ = [
    'SwiftAuth',
    'SwiftObject',
    'SwiftContainer',
    'SwiftService',
    'SwiftNodeFactory'
]
