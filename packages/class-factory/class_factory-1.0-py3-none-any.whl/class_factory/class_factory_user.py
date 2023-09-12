# coding=utf-8
"""
This module contains the class ClassFactoryUser
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from . import BaseClassFactory
from protected_method_metaclass import ProtectedMethodMetaClass, Protected


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =================================================================
class ClassFactoryUser(object, metaclass=ProtectedMethodMetaClass):
    """
    This class represents the base class for classes using a factory for their subclasses
    The following methods have to be overloaded :
        * __get_factory_id
        * __get_import_data_for_factory
        * __get_base_class_for_factory
        * __get_id_function_name_for_factory

    The following methods may be overloaded :
        * __get_handled_exceptions_for_factory
        * __get_id_exception_for_factory
        * add_base_class
    """
    # ==========
    @classmethod
    def get_factory(cls):
        """
        This method is designed to get the factory

        :rtype: BaseClassFactory
        :return: the factory
        """
        key = (cls.__get_factory_id(), cls.__get_base_class_for_factory())
        factory = BaseClassFactory.get_factory_instance(key)
        if factory is None:
            factory = cls.__get_factory()

        return factory

    # ==========
    @classmethod
    def __get_factory(cls):
        """
        This method is designed to generate and get the factory

        :rtype: BaseClassFactory
        :return: the factory
        """
        factory_id = cls.__get_factory_id()
        imports_data = cls.__get_import_data_for_factory()
        base_class = cls.__get_base_class_for_factory()
        id_function_name = cls.__get_id_function_name_for_factory()
        handled_exceptions = cls.__get_handled_exceptions_for_factory()
        id_exception = cls.__get_id_exception_for_factory()
        factory = BaseClassFactory(factory_id, imports_data, base_class, id_function_name,
                                   handled_exceptions=handled_exceptions, id_exception=id_exception)

        return factory

    # ========
    @Protected
    @classmethod
    def __get_factory_id(cls):
        """
        This method is designed to get the ID of the factory dedicated to this class
        The name of the directory where subclasses are to be found is a good idea

        :rtype: str
        :return: the ID of the factory dedicated to this class
        """
        msg = "The method '__get_factory_id' is not overloaded for class %s !"
        msg %= str(cls)
        raise NotImplementedError(msg)

    # ========
    @Protected
    @classmethod
    def __get_import_data_for_factory(cls):
        """
        This method is designed to get the list of settings to import subclasses. Each item of the list contains :
          - import_path : path from which files to import are searched recursively : <import_path>/*/**/<format_name>
          - import_val : string replacing import path to import the files.
            ex : <import_path>/a/b/<file name>
               - if import_val == "":
                 the file will be imported this way : "from a.b import <module name>
               - otherwise:
                   the file will be imported this way  "from <import_val>.a.b import <module name>
          - format_name : glob token used to find the file to import (ex : task_*.py)

        :rtype: list[(str, str, str)]
        :return: the list of settings to import subclasses : (import_path, import_val, format_name)
        """
        msg = "The method '__get_import_data_for_factory' is not overloaded for class %s !"
        msg %= str(cls)
        raise NotImplementedError(msg)

    # ========
    @Protected
    @classmethod
    def __get_base_class_for_factory(cls):
        """
        This method is designed to get the base class for the factory

        :rtype: type
        :return: the base class for the factory
        """
        msg = "The method '__get_base_class_for_factory' is not overloaded for class %s !"
        msg %= cls.__name__
        raise NotImplementedError(msg)

    # ========
    @Protected
    @classmethod
    def __get_id_function_name_for_factory(cls):
        """
        This method is designed to get the name of the method returning the ID of the class for the factory

        :rtype: str
        :return: the name of the method returning the ID of the class for the factory
        """
        msg = "The method '__get_id_function_name_for_factory' is not overloaded for class %s !"
        msg %= cls.__name__
        raise NotImplementedError(msg)

    # ==========
    @classmethod
    def add_base_class(cls):
        """
        This method is designed to know if the base class must be regitred in the factory

        :rtype: bool
        :return: True if the base class must be registred in the factory, False otherwise
        """
        return False

    # ========
    @Protected
    @classmethod
    def __get_handled_exceptions_for_factory(cls):
        """
        This method is designed to get the tuple of exception types to be displayed directly,
        without traceback when there is an import problem

        :rtype handled_exceptions: tuple[Type[Exception]]
        :return: tuple of exception types to be displayed directly, without traceback when there is an import problem
        """
        return tuple()

    # ========
    @Protected
    @classmethod
    def __get_id_exception_for_factory(cls):
        """
        This method is designed to get the Exception or method instanciating an Exception when an ID is not found

        :rtype: NoneType | (str) -> Exception
        :return: Exception or method instanciating an Exception when an ID is not found
        """
        return None


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
