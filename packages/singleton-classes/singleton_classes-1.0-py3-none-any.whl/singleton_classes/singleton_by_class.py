# coding=utf-8
"""
This module contains the classes SingletonByClassMeta and SingletonByClass
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from typing import TypeVar, Type
from .exceptions import SingletonByClassException


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================
SingletonByClass_subclass = TypeVar("SingletonByClass_subclass", bound="SingletonByClass")


# ==================================================================================================
# CLASSES
# ==================================================================================================

# ===============================
class SingletonByClassMeta(type):
    """
    This is the metaclass used for classic Singleton

    Class attributes
    :type __instance_dict: dict[SingletonByClassMeta, SingletonByClass]
    :cvar __instance_dict: dictionnary linking a class to its singleton
    """
    __instance_dict = {}

    # ==========
    @classmethod
    def __get_instance(mcs, the_class):
        """
        This method is designed to get the singleton instance for a class
        None if no instance

        :type the_class: SingletonByClassMeta
        :param the_class: the class trying to get its instance

        :rtype: NoneType | SingletonByClass
        :return: the singleton instance for the class
        """
        return mcs.__instance_dict.get(the_class, None)

    # ==========
    @classmethod
    def __set_instance(mcs, the_class, instance):
        """
        This method is designed to set the singleton instance for a class

        :type the_class: SingletonByClassMeta
        :param the_class: the class trying to set its instance

        :type instance: SingletonByClass
        :param instance: the singleton instance for the class
        """
        mcs.__instance_dict[the_class] = instance

    # ===============================================================================================
    def __call__(cls: Type[SingletonByClass_subclass], *args, **kwargs) -> SingletonByClass_subclass:
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

        :rtype: SingletonByClass
        :return: the singleton instance
        """
        the_instance = cls.__get_instance(cls)
        if the_instance is None:
            res = cls.new_ref_instance(*args, **kwargs)
        elif len(args) + len(kwargs) > 0:
            raise SingletonByClassException(cls)
        else:
            res = the_instance

        return res

    # =======================================================================================================
    def new_ref_instance(cls: Type[SingletonByClass_subclass], *args, **kwargs) -> SingletonByClass_subclass:
        """
        This method is designed to instanciate a new singleton instance and keep it as the reference instance.

        :type args: any
        :param args: arguments for instanciation

        :type kwargs: any
        :param kwargs: keywords arguments for instanciation

        :rtype: SingletonByClass
        :return: the singleton instance
        """
        res = cls.new_unregistered_instance(*args, **kwargs)
        cls.__set_instance(cls, res)

        return res

    # ================================================================================================================
    def new_unregistered_instance(cls: Type[SingletonByClass_subclass], *args, **kwargs) -> SingletonByClass_subclass:
        """
        This method is designed to instanciate a new singleton instance that will not be used as reference instance

        :type args: any
        :param args: arguments for instanciation

        :type kwargs: any
        :param kwargs: keywords arguments for instanciation

        :rtype: SingletonByClass
        :return: the singleton instance
        """
        return type.__call__(cls, *args, **kwargs)


# =============================================================
class SingletonByClass(object, metaclass=SingletonByClassMeta):
    """
    Base class for all singletons by class
    """


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
