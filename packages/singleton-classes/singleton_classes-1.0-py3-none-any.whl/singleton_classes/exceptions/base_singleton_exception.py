# coding=utf-8
"""
This module contains the class BaseSingletonExcetion
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from typing import Generator
from protected_method_metaclass.protected_method_metaclass import Protected, ProtectedMethodMetaClass


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =========================================================================
class BaseSingletonExcetion(Exception, metaclass=ProtectedMethodMetaClass):
    """
    Base class for all Singleton Exceptions

    Class attributes:
    :type __method_token_template: str
    :cvar __method_token_template: template for tokens for special instanciation methods
    """
    __method_token_template = "    - %s :%s"

    # =================
    def __init__(self):
        """
        Initization of a BaseSingletonExcetion instance
        """
        msg = self.__build_msg()
        super().__init__(msg)

    # ==========
    @classmethod
    def __get_metaclass_public_method_names_iterator(cls, the_metaclass):
        """
        This method is designed to get an iterator over the names of the public methods of the metaclass for singleton

        :type the_metaclass: type
        :param the_metaclass: the metaclass for singleton

        :rtype: Generator[str]
        :return: An iterator over the names of the public methods of the metaclass for singleton
        """
        for method_name in the_metaclass.__dict__:
            if not method_name.startswith("_"):
                yield method_name

    # ==========
    @classmethod
    def __get_metaclass_method_doc(cls, the_metaclass, method_name):
        """
        This method is designed to get the formated doc of a method of the indicated metaclass

        :type the_metaclass: type
        :param the_metaclass: the metaclass for singleton

        :type method_name: str
        :param method_name: the name of the method from which doc is taken

        :rtype: str
        :return: The formated doc of the method of the indicated metaclass
        """
        return the_metaclass.__dict__[method_name].__doc__.replace("\n        ", "\n      ")

    # ========
    @Protected
    @classmethod
    def __get_metaclass_public_methods_doc(cls, the_metaclass):
        """
        This method is designed to get the doc for all the public methods of the metaclass for singleton

        :type the_metaclass: type
        :param the_metaclass: the metaclass for singleton

        :rtype: str
        :return: The doc for all the public methods of the metaclass for singleton
        """
        res_list = []
        for method_name in cls.__get_metaclass_public_method_names_iterator(the_metaclass):
            method_doc = cls.__get_metaclass_method_doc(the_metaclass, method_name)
            token = cls.__method_token_template % (method_name, method_doc)
            res_list.append(token)

        return "\n".join(res_list)

    # ========
    @Protected
    def __build_msg(self):
        """
        This method is designed the exception message from the attributes

        :rtype: str
        :return: the exception message from the attributes
        """
        msg = "The method '__build_msg' has not been overloaded for class %s" % str(self.__class__)
        raise NotImplementedError(msg)


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
