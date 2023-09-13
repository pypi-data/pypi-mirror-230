# coding=utf-8
"""
This module contains the class TptNodeMismatchException
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

# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ========================================
class TptNodeMismatchException(Exception):
    """
    Exceptions raised when trying to acces inconsistent data for a TptNode instance

    Class attributes:
    :type __BASE_MSG: str
    :cvar __BASE_MSG: describes this kind of error
    """
    __BASE_MSG = "Inconsistent data access request to a TptNode"

    # ======================
    def __init__(self, msg):
        """
        Initialization of a TptNodeMismatchException instance

        :type msg: str
        :param msg: the contextual error message
        """
        Exception.__init__(self, msg)

    # =================
    def __str__(self):
        """
        Overloaded error message to get the full error message

        :rtype: str
        :return: the full error message
        """
        return self.__BASE_MSG + '\n\t' + self.args[0]


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
