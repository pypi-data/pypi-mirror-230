# coding=utf-8
"""
__init__ module for package protected_method_metaclass
"""
__author__ = 'Marc MALBERT'
__email__ = 'eldrad-59@hotmail.fr'
__version__ = '1.0'
__maintainer__ = 'Marc MALBERT'
__date__ = '12/12/2018'

# ==================================================================================================
# IMPORTS
# ==================================================================================================
from .protected_decorator import Protected
from .protected_method_metaclass import ProtectedMethodMetaClass
try:
    from .protected_method_metaclass_qt import ProtectedMethodMetaClass_Qt
except Exception:
    pass
try:
    from .protected_method_metaclass_pyside2 import ProtectedMethodMetaClass_PySide2
except Exception:
    pass


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ==================================================================================================
# FONCTIONS
# ==================================================================================================
