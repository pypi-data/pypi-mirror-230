# coding=utf-8
"""
This module contains the class TptRootNode
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
from tpt_reading import TptNodeMismatchException
from .tpt_node import TptNode


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =========================
class TptRootNode(TptNode):
    """
    This class defines root nodes for template reading.

    Instance attributes
    :type __filepath: str
    :ivar __filepath: the path to the template file
    """

    # ===========================
    def __init__(self, filepath):
        """
        Initialization of TptRootNode instance

        :type filepath: str
        :param filepath:  the path to the template file
        """
        TptNode.__init__(self, "root_node", [], None)
        self.__filepath = filepath
        self.__load_file()

    # =====================
    def get_filepath(self):
        """
        This method is designed to get the path to the template file

        :rtype: str
        :return: the path to the template file
        """
        return self.__filepath

    # ====================
    def __load_file(self):
        """
        This method is designed to load the template file
        """
        f = open(self.__filepath, 'r', encoding='utf-8')
        line = f.readline()
        if line.strip() != "[ROOT]":
            f.close()
            msg = "no ROOT node in the template !"
            raise TptNodeMismatchException(msg)
        line = f.readline()
        striped_line = line.strip()
        while striped_line != "[/ROOT]":
            if striped_line.startswith("[BLOC"):
                bloc_tag = striped_line[1:-1]
                test_splits = bloc_tag.split(" ")
                bloc_name = test_splits[0]
                bloc_args = test_splits[1:]
                line = self.__read_bloc(bloc_name, bloc_args, f, self)
                striped_line = line.strip()
        f.close()

    # ================================================
    def generate_example(self, output_path, css_name):
        """
        This method is designed to generate the exemple file for this TptRootNode

        :type output_path: str
        :param output_path: path to the output file

        :type css_name: str
        :param css_name: name of the css to used
        """
        txt = self.get_example_text()
        txt = txt.replace("@css_file@", css_name)
        f = open(output_path, "w", encoding='utf-8')
        f.write(txt)
        f.close()


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
