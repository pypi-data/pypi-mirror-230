# coding=utf-8
"""
This module contains the class BaseClassFactory
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from typing import Type
import os
import glob
import traceback
from typing import Generator, Iterable
from importlib import import_module


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =============================
class BaseClassFactory(object):
    """
    This class represents factorys gathering sub classes of a parent class

    Class attributes:
    :type __instances: dict[(str, Type[class_factory.ClassFactoryUser]), BaseClassFactory]
    :cvar __instances: dictionnary linking the id of the factory and a parent class to the matching BaseClassFactory instance


    Instance factory:
    :type __handled_exceptions: NoneType | tuple[Type[Exception]]
    :ivar __handled_exceptions: tuple of exception types to be displayed directly, without traceback when there is an import problem

    :type __factory_id: str
    :ivar __factory_id: An Id for the factory. The name of the directorory where child classes are to be found is a good idea

    :type __base_class: Type[class_factory.ClassFactoryUser]
    :ivar __base_class: the parent class

    :type __imports_data: list[(str, str, str)]
    :ivar __imports_data: list of settings to import subclasses. Each item of the list contains :
                              - format_name : glob token used to find the file to import (ex : task_*.py)
                              - import_path : path from which files to import are searched recursively : <import_path>/*/**/<format_name>
                              - import_val : string replacing import path to import the files.
                                ex : <import_path>/a/b/<file name>
                                   - if import_val == "":
                                     the file will be imported this way : "from a.b import <module name>
                                   - otherwise:
                                       the file will be imported this way  "from <import_val>.a.b import <module name>

    :type __id_function_name: str
    :ivar __id_function_name: name of the function used to get the ID of the subclasses

    :type __name_to_class: dict[str, Type[class_factory.ClassFactoryUser]]
    :ivar __name_to_class: dictionnary linking the ID of a subclass to the subclass

    :type __id_exception: NoneType | (str) -> Exception
    :ivar __id_exception: Exception or method instanciating an Exception when an ID is not found

    :type __load: bool
    :ivar __load: True if the factory loads all subclasses when it is initialized, False otherwise

    :type __alias_dict: dict[str, Iterable[str]]
    :ivar __alias_dict: dictionnary linking an ID to its alias list
    """
    __instances = {}

    # =============================================================================================================================
    def __new__(cls, factory_id, imports_data, base_class, id_function_name, handled_exceptions=None, id_exception=None, load=True,
                alias_dict=None):
        """
        Overloaded __new__ method used to update the __instances class attribute

        :type factory_id: str
        :param factory_id: An Id for the factory. The name of the directorory where child classes are to be found is a good idea

        :type imports_data: list[(str, str, str)]
        :param imports_data: list of settings to import subclasses. Each item of the list contains :
                              - format_name : glob token used to find the file to import (ex : task_*.py)
                              - import_path : path from which files to import are searched recursively : <import_path>/*/**/<format_name>
                              - import_val : string replacing import path to import the files.
                                ex : <import_path>/a/b/<file name>
                                   - if import_val == "":
                                     the file will be imported this way : "from a.b import <module name>
                                   - otherwise:
                                       the file will be imported this way  "from <import_val>.a.b import <module name>

        :type base_class: Type[class_factory.ClassFactoryUser]
        :param base_class: the parent class

        :type id_function_name: str
        :param id_function_name: name of the function used to get the ID of the subclasses

        :type handled_exceptions: NoneType | tuple[Type[Exception]]
        :param handled_exceptions: tuple of exception types to be displayed directly, without traceback when there is an import problem

        :type id_exception: NoneType | (str) -> Exception
        :param id_exception: Exception or method instanciating an Exception when an ID is not found

        :type load: bool
        :ivar load: True if the factory loads all subclasses when it is initialized, False otherwise

        :type alias_dict: dict[str, Iterable[str]]
        :ivar alias_dict: dictionnary linking an ID to its alias list
        """
        key = (factory_id, base_class)
        try:
            res = cls.__instances[key]
        except KeyError:
            res = object.__new__(cls)

        return res

    # ==========
    @classmethod
    def get_factory_instance(cls, key):
        """
        This method is designed to get an instance of BaseClassFactory from its key if it allready exists
        Otherwise, None is returned

        :type key: (str, Type[class_factory.ClassFactoryUser])
        :param key: (the id of the factory, a parent class)

        :rtype: NoneType | BaseClassFactory
        :return: the matching BaseClassFactory instance
        """
        try:
            res = cls.__instances[key]
        except KeyError:
            res = None

        return res

    # ==========
    @classmethod
    def __set_instance(cls, the_instance):
        """
        This method is designed to update/set the __instances class attribute from a BaseClassFactory instance

        :type the_instance: BaseClassFactory
        :param the_instance: the BaseClassFactory instance
        """
        key = (the_instance.__factory_id, the_instance.__base_class)
        cls.__instances[key] = the_instance

    # ===============================================================================================================================
    def __init__(self, factory_id, imports_data, base_class, id_function_name, handled_exceptions=None, id_exception=None, load=True,
                 alias_dict=None):
        """
        Initialization of a BaseClassFactory instance

        :type factory_id: str
        :param factory_id: An Id for the factory. The name of the directorory where child classes are to be found is a good idea

        :type imports_data: list[(str, str, str)]
        :param imports_data: list of settings to import subclasses. Each item of the list contains :
                              - format_name : glob token used to find the file to import (ex : task_*.py)
                              - import_path : path from which files to import are searched recursively : <import_path>/*/**/<format_name>
                              - import_val : string replacing import path to import the files.
                                ex : <import_path>/a/b/<file name>
                                   - if import_val == "":
                                     the file will be imported this way : "from a.b import <module name>
                                   - otherwise:
                                       the file will be imported this way  "from <import_val>.a.b import <module name>

        :type base_class: Type[class_factory.ClassFactoryUser]
        :param base_class: the parent class

        :type id_function_name: str
        :param id_function_name: name of the function used to get the ID of the subclasses

        :type handled_exceptions: NoneType | tuple[Type[Exception]]
        :param handled_exceptions: tuple of exception types to be displayed directly, without traceback when there is an import problem

        :type id_exception: NoneType | (str) -> Exception
        :param id_exception: Exception or method instanciating an Exception when an ID is not found

        :type load: bool
        :ivar load: True if the factory loads all subclasses when it is initialized, False otherwise

        :type alias_dict: dict[str, Iterable[str]]
        :ivar alias_dict: dictionnary linking an ID to its alias list
        """
        key = (factory_id, base_class)
        if self.get_factory_instance(key) is None:
            if handled_exceptions is None:
                handled_exceptions = tuple()
            if alias_dict is None:
                alias_dict = {}

            self.__id_exception = id_exception
            self.__handled_exceptions = handled_exceptions
            self.__factory_id = factory_id
            self.__base_class = base_class
            self.__imports_data = imports_data
            self.__id_function_name = id_function_name
            self.__name_to_class = {}
            self.__load = load
            self.__alias_dict = alias_dict

            if load:
                self.__import_classes()
            self.__set_instance(self)

    # =========================
    def __import_classes(self):
        """
        This method is designed to register all sub classes
        """
        if self.__base_class.add_base_class():
            get_id_func = getattr(self.__base_class, self.__id_function_name)
            functionnality_name = get_id_func()
            self.__name_to_class[functionnality_name] = self.__base_class

        for (import_path, import_val, format_name) in self.__imports_data:
            for module_path in glob.iglob(os.path.join(import_path, "*/**", format_name), recursive=True):
                self.__import_from_module(module_path, import_path, import_val)

    # ===================================================================
    def __import_from_module(self, module_path, import_path, import_val):
        """
        This method is designed to register the subclass in the pointed module

        :type module_path: str
        :param module_path: the path to the module

        :type import_path : str
        :param import_path: path from which files to import are searched recursively : <import_path>/*/**/<format_name>

        :type import_val : str
        :param import_val : string replacing import path to import the files.
                            ex : <import_path>/a/b/<file name>
                               - if import_val == "":
                                 the file will be imported this way : "from a.b import <module name>
                               - otherwise:
                                   the file will be imported this way  "from <import_val>.a.b import <module name>

        :rtype: NoneType | Type[class_factory.ClassFactoryUser]
        :return: None if no class is found, the found class otherwise
        """
        res = None
        package_import = os.path.dirname(module_path).replace(import_path, "").replace(os.sep, ".")
        module_name = os.path.basename(module_path).split(".")[0]
        if import_val == "":
            module_path = "%s.%s" % (package_import[1:], module_name)
        else:
            module_path = "%s%s.%s" % (import_val, package_import, module_name)

        try:
            module_object = import_module(module_path)
        except self.__handled_exceptions as e:
            print("import failed : %s" % module_path)
            print("    " + str(e).replace("\n", "\n    "))
        except Exception:
            print("import failed : %s" % module_path)
            print("    " + traceback.format_exc().replace("\n", "\n    "))
        else:
            for name, test_item in module_object.__dict__.items():
                if isinstance(test_item, type):
                    if test_item.__module__ == module_object.__name__:
                        if issubclass(test_item, self.__base_class):
                            if test_item != self.__base_class:
                                get_id_func = getattr(test_item, self.__id_function_name)
                                functionnality_name = get_id_func()
                                self.__name_to_class[functionnality_name] = test_item
                                res = test_item

        return res

    # ====================================
    def get_class_from_id(self, class_id):
        """
        This method is desigend to get a subclass from its ID or alias

        :type class_id: str
        :param class_id: the id of the subclass

        :rtype: Type[class_factory.ClassFactoryUser]
        :return: the subvlass matching the id or alias
        """
        try:
            res = self.__name_to_class[class_id]
        except KeyError:
            if self.__load:
                exception = self.__get_id_error(class_id)
                raise exception
            else:
                alias_list = [class_id]
                try:
                    aliases = self.__alias_dict[class_id]
                except KeyError:
                    pass
                else:
                    for elem in aliases:
                        alias_list.insert(0, elem)

                res = None
                for (import_path, import_val, format_name) in self.__imports_data:
                    idx = format_name.find("*")
                    if idx != -1:
                        for alias in alias_list:
                            new_format_name = self.__get_new_format_name(format_name, alias, idx)
                            for module_path in glob.iglob(os.path.join(import_path, "*/**", new_format_name), recursive=True):
                                res = self.__import_from_module(module_path, import_path, import_val)
                                if res is not None:
                                    break
                            if res is not None:
                                break
                    else:
                        msg = "File format '%s' is not compatible with this import mode" % class_id
                        raise Exception(msg)

                if res is None:
                    exception = self.__get_id_error(class_id)
                    raise exception

        return res

    # ===========
    @staticmethod
    def __get_new_format_name(format_name, alias, idx):
        """
        This method is designed to get the modified format_name to take alias into account
        the "underscore cas" conversino is automatically taken into account.

        :type format_name: str
        :param format_name: format_name as defined for this instance

        :type alias: str
        :param alias: the used alias

        :type idx: int
        :param idx: position of the charater to be replaced by the alias

        :rtype: str
        :return: the modified format_name to take alias into account
        """
        new_alias = alias[0].lower()
        for char in alias[1:]:
            if char.isupper():
                new_alias += "_" + char.lower()
            else:
                new_alias += char

        new_format_name = format_name[:idx] + new_alias + format_name[idx + 1:]

        return new_format_name

    # =================================
    def __get_id_error(self, class_id):
        """
        This method is designed to get the exception linked to an ID problem

        :type class_id: str
        :param class_id: the ID that causing trouble

        :rtype: Exception
        :return: The Exception to raise
        """
        if self.__id_exception is None:
            msg = "%s is not a valid ID" % class_id
            res = Exception(msg)
        else:
            res = self.__id_exception(class_id)

        return res

    # ========================================================
    def get_instance_from_id(self, class_id, *args, **kwargs):
        """
        This method is desigend to get an instance of a subclass from its ID or alias and arguments

        :type class_id: str
        :param class_id: the id of the subclass

        :type args: any
        :param args: positional arguments for the instance

        :type kwargs: any
        :param kwargs: keyword arguments for the instance

        :rtype: class_factory.ClassFactoryUser
        :return: the desired subclass instance
        """
        the_class = self.get_class_from_id(class_id)

        return the_class(*args, **kwargs)

    # =========================
    def get_ids_iterator(self):
        """
        This method is designed to get an iterator over the IDs of the subclasses

        :rtype: Generator[str]
        :return:  an iterator over the IDs of the subclasses
        """
        for elem in self.__name_to_class:
            yield elem

    # ================
    def get_ids(self):
        """
        This method is designed to get the list of IDs of the subclasses

        :rtype: list[str]
        :return: the list of IDs of the subclasses
        """
        return [elem for elem in self.get_ids_iterator()]


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
