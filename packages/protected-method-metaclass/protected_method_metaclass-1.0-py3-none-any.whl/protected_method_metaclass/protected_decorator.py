# coding=utf-8
"""
This module contains the Protected class
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================

# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ======================
class Protected(object):
    """
    This class is designed to create objects containing a function
    It is used as a decorator in conjonction with the ProtectedMethodMetaclass
    to allow the protected mecanism

    Instance attributes:
    :type __f: any
    :ivar __f: the function/classmethod/staticmethod to make protected
    """
    # ====================
    def __init__(self, f):
        """
        Initialization of a Protected instance

        :type f: any
        :param f: the function/classmethod/staticmethod to make protected
        """
        self.__f = f

    # ==============
    def get_f(self):
        """
        This method is designed to return the contained function

        :rtype: any
        :return: the function/classmethod/staticmethod to make protected
        """
        return self.__f


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
