# coding=utf-8
"""
This module contains the class TptDataNode
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
from tpt_reading import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from .tpt_node import TptNode


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =========================
class TptDataNode(TptNode):
    """
    This class defines nodes containing data

    Instance attributes:
    :type __data: str
    :ivar __data: The text content of the node from the template
    """

    # ===============================
    def __init__(self, parent, data):
        """
        Initialization of a TptDataNode instance

        :type parent: TptNode
        :param parent: the parent node

        :type data: str
        :param data: The text content of the node from the template
        """
        TptNode.__init__(self, "data_node", [], parent)
        self.__data = data

    # =================
    def get_data(self):
        """
        This method is designed to get the text content of the node from the template

        :rtype: str
        :return: The text content of the node from the template
        """
        return self.__data

    # ===========================================
    def get_text(self, data_dict, _ref_item):
        """
        This method is designed to get the content of the node updated with the data

        :type data_dict: dict[str: str]
        :param data_dict: dictionnary containing complementary data

        :type _ref_item: hierarchical_storage.HierarchicalNode
        :param _ref_item: the HierarchicalNode containing the data
                          (unused here but required for inheritance)

        :rtype: str
        :return: the content of the node updated with the data
        """
        s = ''
        data = self.__data
        for key in data_dict:
            data = data.replace("@" + key + "@", data_dict[key])
        s += data
        return s

    # =========================
    def get_example_text(self):
        """
        This method is designed to get the exemple text of this node

        :rtype: str
        :return: the exemple text of this node
        """
        return self.__data


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
