# coding=utf-8
"""
This module contains the ProtectedMethodMetaClass_PySide2 class
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from .protected_method_metaclass import ProtectedMethodMetaClass
from PySide2.QtWidgets import QWidget as PySideWidget


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================
pysideWrapperType = type(PySideWidget)


# ==================================================================================================
# CLASSES
# ==================================================================================================

# ===================================================================================
class ProtectedMethodMetaClass_PySide2(pysideWrapperType, ProtectedMethodMetaClass):
    """
    This metaclass has exactly the same role as the ProtectedMethodMetaClass
    but for classes inheriting from a PySide2 class.
    """

    # ============================================
    def __new__(mcs, classname, bases, classdict):
        """
        __new__ method of the metaclasse

        :type classname: str
        :param classname: the name of the class to be created

        :type bases: tuple[type]
        :param bases: the parent classes of the classes to be created

        :type classdict: dict
        :param classdict: the dict of the class to be created

        :rtype: MetaClassForProtected
        :return: the class create through metaclass
        """
        ProtectedMethodMetaClass.__new__(mcs, classname, bases, classdict, no_return=True)
        return pysideWrapperType.__new__(mcs, classname, bases, classdict)

# ==================================================================================================
# FONCTIONS
# ==================================================================================================
