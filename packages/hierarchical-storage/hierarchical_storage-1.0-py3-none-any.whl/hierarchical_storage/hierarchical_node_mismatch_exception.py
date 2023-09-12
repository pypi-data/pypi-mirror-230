# coding=utf-8
"""
This module contains the HierarchicalNodeMismatchException class
"""

# ========================================================================================
#  _    _ _                         _     _       _       _
# | |  | (_)                       | |   (_)     | |     | |
# | |__| |_  ___ _ __ __ _ _ __ ___| |__  _  __ _| |  ___| |_ ___  _ __ __ _  __ _  ___
# |  __  | |/ _ \ '__/ _` | '__/ __| '_ \| |/ _` | | / __| __/ _ \| '__/ _` |/ _` |/ _ \
# | |  | | |  __/ | | (_| | | | (__| | | | | (_| | | \__ \ || (_) | | | (_| | (_| |  __/
# |_|  |_|_|\___|_|  \__,_|_|  \___|_| |_|_|\__,_|_| |___/\__\___/|_|  \__,_|\__, |\___|
#                                                                             __/ |
#                                                                            |___/
# ========================================================================================
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

# =================================================
class HierarchicalNodeMismatchException(Exception):
    """
    This class defines exceptions thrown when attempting to acces inconsistent data from a HierarchicalNode

    Class Attributes:
    :type __BASE_MSG: str
    :cvar __BASE_MSG: Description of a HierarchicalNodeMismatchException
    """
    __BASE_MSG = "Inconsistent data request for a HierarchicalNode"

    # ======================
    def __init__(self, msg):
        """
        Initialisation of a HierarchicalNodeMismatchException instance

        :type msg: str
        :param msg: the contextual error message
        """
        Exception.__init__(self, msg)

    # =================
    def __str__(self):
        """
        Overloaded __str__ method

        :rtype: str
        :return: the complete error message
        """
        return self.__BASE_MSG + '\n\t' + self.args[0]


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
