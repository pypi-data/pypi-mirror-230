# coding=utf-8
"""
This module contains the class SingletonException
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from typing import Type, TypeVar
from .base_singleton_exception import BaseSingletonExcetion


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================
Singleton_subclass = TypeVar("Singleton_subclass", bound="Singleton")


# ==================================================================================================
# CLASSES
# ==================================================================================================


# ==============================================
class SingletonException(BaseSingletonExcetion):
    """
    This class represents exceptions raised when the Singleton mecanism fails

    Class attributes:
    :type __msg_template_list: list[str]
    :cvar __msg_template_list: list of text used as template to geneate the message of an exception


    Instance attributes:
    :type __the_class: singletons.singleton.SingletonMeta
    :ivar __the_class: the class that created the exception
    """
    __msg_template_list = ["%s has been called with arguments. Unauthorized operation for Singleton sub classes !",
                           "Use the following methods :"]

    # ================================================
    def __init__(self, the_class: Type[Singleton_subclass]):
        """
        Initialization of a SingletonException instance

        :type the_class: singletons.singleton.SingletonMeta
        :param the_class: the class that created the exception
        """
        self.__the_class = the_class  # type:  Type[Singleton_subclass]
        super().__init__()

    # ==============================================
    def get_class(self) -> Type[Singleton_subclass]:
        """
        This method is designed to get the class that created the exception

        :rtype: singletons.singleton.SingletonMeta
        :return: the class that created the exception
        """
        return self.__the_class

    # ====================
    def __build_msg(self):
        """
        This method is designed the exception message from the attributes

        :rtype: str
        :return: the exception message from the attributes
        """
        msg_list = [self.__msg_template_list[0] % str(self.__the_class),
                    self.__msg_template_list[1],
                    self.__get_metaclass_public_methods_doc(type(self.__the_class))]

        return "\n".join(msg_list)


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
