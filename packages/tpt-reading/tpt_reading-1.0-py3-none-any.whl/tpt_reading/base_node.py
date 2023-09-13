# coding=utf-8
"""
This module contains the class BaseNode
"""
# =============================================================================================== #
#   _______    _     _____                _ _
#  |__   __|  | |   |  __ \              | (_)
#     | |_ __ | |_  | |__) |___  __ _  __| |_ _ __   __ _
#     | | '_ \| __| |  _  // _ \/ _` |/ _` | | '_ \ / _` |
#     | | |_) | |_  | | \ \  __/ (_| | (_| | | | | | (_| |
#     |_| .__/ \__| |_|  \_\___|\__,_|\__,_|_|_| |_|\__, |
#       | |                                          __/ |
#       |_|                                         |___/
# =============================================================================================== #
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
import os
from class_factory import ClassFactoryUser


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ===============================
class BaseNode(ClassFactoryUser):
    """
    This class is the base class for all node and grant them the factory mechanism
    """
    # ==========
    @classmethod
    def __get_factory_id(cls):
        """
        This method is designed to get the ID of the factory dedicated to this class
        The name of the directory where subclasses are to be found is a good idea

        :rtype: str
        :return: the ID of the factory dedicated to this class
        """
        return "tpt_reading/nodes"

    # ==========
    @classmethod
    def __get_import_data_for_factory(cls):
        """
        This method is designed to get the list of settings to import subclasses. Each item of the list contains :
          - format_name : glob token used to find the file to import (ex : task_*.py)
          - import_path : path from which files to import are searched recursively : <import_path>/*/**/<format_name>
          - import_val : string replacing import path to import the files.
            ex : <import_path>/a/b/<file name>
               - if import_val == "":
                 the file will be imported this way : "from a.b import <module name>
               - otherwise:
                   the file will be imported this way  "from <import_val>.a.b import <module name>

        :rtype: list[(str, str, str)]
        :return: the list of settings to import subclasses : (import_path, import_val, format_name)
        """
        tpt_reading_dir_path = os.path.dirname(os.path.abspath(__file__))
        import_val = "tpt_reading"

        res = [(tpt_reading_dir_path, import_val, "*.py")]

        return res

    # ==========
    @classmethod
    def __get_base_class_for_factory(cls):
        """
        This method is designed to get the base class for the factory

        :rtype: type
        :return: the base class for the factory
        """
        return BaseNode

    # ==========
    @classmethod
    def __get_id_function_name_for_factory(cls):
        """
        This method is designed to get the name of the method returning the ID of the class for the factory

        :rtype: str
        :return: the name of the method returning the ID of the class for the factory
        """
        return "get_node_class_id"

    # ==========
    @classmethod
    def get_node_class_id(cls):
        """
        This method is designed to get the ID for the factory

        :rtype: str
        :return: the ID for the factory
        """
        return cls.__name__


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
