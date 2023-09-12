# coding=utf-8
"""
This module contains the class SingletonByClassAndIdException
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from typing import Hashable, Type, TypeVar
from .base_singleton_exception import BaseSingletonExcetion


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================
SingletonByClassAndId_subclass = TypeVar("SingletonByClassAndId_subclass", bound="SingletonByClassAndId")


# ==================================================================================================
# CLASSES
# ==================================================================================================

# ==========================================================
class SingletonByClassAndIdException(BaseSingletonExcetion):
    """
    This class represents exceptions raised when the SingletonByClassAndId mecanism fails

    Class attributes:
    :type __msg_template_list: list[str]
    :cvar __msg_template_list: list of text used as template to geneate the message of an exception


    Instance attributes:
    :type __the_class: singletons.singleton_by_class_and_id.SingletonByClassAndIdMeta
    :ivar __the_class: the class that created the exception

    :type __the_id: Hashable
    :ivar __the_id: the id that created the exception
    """
    __msg_template_list = ["%s has been called with more arguments than just id. "
                           "Unauthorized operation for SingletonByClassAndId sub classes !",
                           "Use the following methods :"]

    # ==========================================================================
    def __init__(self, the_class: Type[SingletonByClassAndId_subclass], the_id):
        """
        Initialization of a SingletonException instance

        :type the_class: singletons.singleton_by_class_and_id.SingletonByClassAndIdMeta
        :param the_class: the class that created the exception

        :type the_id: Hashable
        :param the_id: The id that created the exception
        """
        self.__the_class = the_class  # type: Type[SingletonByClassAndId_subclass]
        self.__the_id = the_id
        super().__init__()

    # ==========================================================
    def get_class(self) -> Type[SingletonByClassAndId_subclass]:
        """
        This method is designed to get the class that created the exception

        :rtype: singletons.singleton_by_class_and_id.SingletonByClassAndIdMeta
        :return: the class that created the exception
        """
        return self.__the_class

    # ===============
    def get_id(self):
        """
        This method is designed to get the id that created the exception

        :rtype: Hashable
        :return: the id that created the exception
        """
        return self.__the_id

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
