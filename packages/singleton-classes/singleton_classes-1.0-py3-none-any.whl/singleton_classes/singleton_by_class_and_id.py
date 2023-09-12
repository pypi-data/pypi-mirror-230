# coding=utf-8
"""
This module contains the classes SingletonByClassAndIdMeta and SingletonByClassAndId
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from typing import Hashable, TypeVar, Type, Generic, Union
from .exceptions import SingletonByClassAndIdException


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================
SingletonByClassAndId_subclass = TypeVar("SingletonByClassAndId_subclass", bound="SingletonByClassAndId")
T = TypeVar("T", bound=Hashable)


# ==================================================================================================
# CLASSES
# ==================================================================================================

# ====================================
class SingletonByClassAndIdMeta(type):
    """
    This is the metaclass used for classic Singleton

    Class attributes
    :type __instance_dict: dict[SingletonByClassAndIdMeta, dict[Hashable, SingletonByClassAndId]]
    :cvar __instance_dict: dictionnary linking a class to a dictionnary linking id to its singleton
    """
    __instance_dict = {}

    # ==========
    @classmethod
    def __get_instance(mcs, the_class, the_id):
        """
        This method is designed to get the singleton instance for a class and an id
        None if no instance

        :type the_class: SingletonByClassMeta
        :param the_class: the class trying to get its instance

        :type the_id: Hashable
        :param the_id: the id of the instance

        :rtype: NoneType | SingletonByClassAndId
        :return: the singleton instance for the class
        """
        class_dict = mcs.__instance_dict.get(the_class, {})

        return class_dict.get(the_id, None)

    # ==========
    @classmethod
    def __set_instance(mcs, the_class, the_id, instance):
        """
        This method is designed to set the singleton instance for a class

        :type the_class: SingletonByClassMeta
        :param the_class: the class trying to set its instance

        :type the_id: Hashable
        :param the_id: the id of the instance

        :type instance: Singleton
        :param instance: the singleton instance for the class
        """
        class_dict = mcs.__instance_dict.setdefault(the_class, {})
        class_dict[the_id] = instance

    # =================================================================================================================
    def __call__(cls: Type[SingletonByClassAndId_subclass], the_id, *args, **kwargs) -> SingletonByClassAndId_subclass:
        """
        Overloaded __call__ method to enable singleton mecanism

        NOTE :
        Getting the current instance is performed by calling the class with no only id argument
        If additional arguments are given, the __call__ method will raise an exception if there is already an instance.
        Use new_ref_instance and new_unregistered_instance to generate new instances

        :type the_id: Hashable
        :param the_id: id of the instance

        :type args: any
        :param args: other arguments for instanciation

        :type kwargs: any
        :param kwargs: keywords arguments for instanciation

        :rtype: SingletonByClassAndId
        :return: the singleton instance
        """
        the_instance = cls.__get_instance(cls, the_id)
        if the_instance is None:
            res = cls.new_ref_instance(the_id, *args, **kwargs)
        elif len(args) + len(kwargs) > 0:
            raise SingletonByClassAndIdException(cls, the_id)
        else:
            res = the_instance

        return res

    # =========================================================================================================================
    def new_ref_instance(cls: Type[SingletonByClassAndId_subclass], the_id, *args, **kwargs) -> SingletonByClassAndId_subclass:
        """
        This method is designed to instanciate a new singleton instance and keep it as the reference instance.

        :type the_id: Hashable
        :param the_id: id of the instance

        :type args: any
        :param args: other arguments for instanciation

        :type kwargs: any
        :param kwargs: keywords arguments for instanciation

        :rtype: SingletonByClassAndId
        :return: the singleton instance
        """
        res = cls.new_unregistered_instance(the_id, *args, **kwargs)
        cls.__set_instance(cls, the_id, res)

        return res

    # ==========================================================================================================================
    def new_unregistered_instance(cls: Type[SingletonByClassAndId_subclass], *args, **kwargs) -> SingletonByClassAndId_subclass:
        """
        This method is designed to instanciate a new singleton instance that will not be used as reference instance

        :type args: any
        :param args: arguments for instanciation

        :type kwargs: any
        :param kwargs: keywords arguments for instanciation

        :rtype: SingletonByClassAndId
        :return: the singleton instance
        """
        return type.__call__(cls, *args, **kwargs)


# ===========================================================================
class SingletonByClassAndId(Generic[T], metaclass=SingletonByClassAndIdMeta):
    """
    Base class for all singletons by class and id

    Instance attributes
    :type __singleton_id: Hashable
    :ivar __singleton_id: the singleton Id of the instance
    """
    # ===============================
    def __init__(self, singleton_id):
        """
        Initialization of a SingletonByClassAndId instance

        :type singleton_id: Hashable
        :param singleton_id: The singleton Id of the instance
        """
        self.__singleton_id = singleton_id

    # ==============================
    def get_singleton_id(self) -> T:
        """
        This method is designed to get the singleton Id of the instance

        :rtype: Hashable
        :return: The singleton Id of the instance
        """
        return self.__singleton_id


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
