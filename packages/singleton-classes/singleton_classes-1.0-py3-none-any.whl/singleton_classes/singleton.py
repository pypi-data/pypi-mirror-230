# coding=utf-8
"""
This module contains the classes SingletonMeta and Singleton
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from typing import TypeVar, Type
from .exceptions import SingletonException


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================
Singleton_subclass = TypeVar("Singleton_subclass", bound="Singleton")


# ==================================================================================================
# CLASSES
# ==================================================================================================


# ========================
class SingletonMeta(type):
    """
    This is the metaclass used for classic Singleton

    Class attributes
    :type __instance: NoneType | Singleton
    :cvar __instance: the singleton instance of Singleton
    """
    __instance = None

    # ==========
    @classmethod
    def __get_instance(mcs):
        """
        This method is designed to get the singleton instance
        None if no instance

        :rtype: NoneType | Singleton
        :return: the singleton instance of Singleton
        """
        return mcs.__instance

    # ==========
    @classmethod
    def __set_instance(mcs, instance):
        """
        This method is designed to set the singleton instance

        :type instance: Singleton
        :param instance: the singleton instance of Singleton
        """
        mcs.__instance = instance

    # =================================================================================
    def __call__(cls: Type[Singleton_subclass], *args, **kwargs) -> Singleton_subclass:
        """
        Overloaded __call__ method to enable singleton mecanism

        NOTE :
        Getting the current instance is performed by calling the class with no argument
        If arguments are given, the __call__ method will raise an exception if there is already an instance.
        Use new_ref_instance and new_unregistered_instance to generate new instances

        :type args: any
        :param args: arguments for instanciation

        :type kwargs: any
        :param kwargs: keywords arguments for instanciation

        :rtype: Singleton
        :return: the singleton instance
        """
        the_instance = cls.__get_instance()
        if the_instance is None:
            res = cls.new_ref_instance(*args, **kwargs)
        elif len(args) + len(kwargs) > 0:
            raise SingletonException(cls)
        else:
            res = the_instance

        return res

    # =========================================================================================
    def new_ref_instance(cls: Type[Singleton_subclass], *args, **kwargs) -> Singleton_subclass:
        """
        This method is designed to instanciate a new singleton instance and keep it as the reference instance.

        :type args: any
        :param args: arguments for instanciation

        :type kwargs: any
        :param kwargs: keywords arguments for instanciation

        :rtype: Singleton
        :return: the singleton instance
        """
        res = cls.new_unregistered_instance(*args, **kwargs)
        cls.__set_instance(res)

        return res

    # ==================================================================================================
    def new_unregistered_instance(cls: Type[Singleton_subclass], *args, **kwargs) -> Singleton_subclass:
        """
        This method is designed to instanciate a new singleton instance that will not be used as reference instance

        :type args: any
        :param args: arguments for instanciation

        :type kwargs: any
        :param kwargs: keywords arguments for instanciation

        :rtype: Singleton
        :return: the singleton instance
        """
        return type.__call__(cls, *args, **kwargs)


# ===============================================
class Singleton(object, metaclass=SingletonMeta):
    """
    Base class for all singletons
    """


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
