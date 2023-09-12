# coding=utf-8
"""
This module contains the HierarchicalNode class
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
from typing import Generator
from named_sequence import NamedSequence
from .hierarchical_node_mismatch_exception import HierarchicalNodeMismatchException


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# =============================
class HierarchicalNode(object):
    """
    This class defines nodes for hierarchical data. The hierarchy is divided into categoies meaning a Node can contain
    some nodes regarding to a categoy and other nodes regarding to another category.


    Instance attributes:
    :type __name: str
    :ivar __name: the name of the node

    :type __node_category: str
    :ivar __node_category: the category of the node

    :type __parent: NoneType | HierarchicalNode
    :ivar __parent: the parent of this node

    :type __children_dict: dict[str, NamedSequence[HierarchicalNode]]
    :ivar __children_dict: dictonnary linking a category name to a NamedSequence of HierarchicalNode of this category

    :type __data_dict: dict[str, any]
    :ivar __data_dict: dictionnary of the data contained by the node
    """

    # ===================================================
    def __init__(self, node_category, name, parent=None):
        """
        Initialization of a HierarchicalNode instance

        :type node_category: str
        :param node_category: the category of the node

        :type name: str
        :param name: the name of the node

        :type parent: NonetType | HierarchicalNode
        :param parent: the parent of this node
        """
        self.__node_category = node_category
        self.__name = name
        self.__parent = parent
        self.__children_dict = {}
        self.__data_dict = {}
        if parent is not None:
            parent.add_child(self)

    # =================
    def get_name(self):
        """
        This method is designed to get the name of the node

        :rtype: str
        :return: the name of the node
        """
        return self.__name

    # ==========================
    def get_node_category(self):
        """
        This method is desigend to get the category of the node

        :rtype: str
        :return: the category of the node
        """
        return self.__node_category

    # ====================================
    def set_node_category(self, category):
        """
        This method is designed to update the category of the node

        :type category: str
        :param category: the new category of the node
        """
        parent = self.__parent
        if self.__parent is not None:
            self.set_parent(None)
        self.__node_category = category
        self.set_parent(parent)

    # ===================
    def get_parent(self):
        """
        This method is designed to get the parent of this node

        :rtype: NoneType | HierarchicalNode
        :return: The parent of this node
        """
        return self.__parent

    # ===============================
    def set_parent(self, new_parent):
        """
        This method is designed to set the parent of this HierarchicalNode

        :type new_parent: NoneType | HierarchicalNode
        :param new_parent: the new parent of this HierarchicalNode
        """
        old_parent = self.__parent
        if old_parent != new_parent:
            self.__parent = new_parent
            if old_parent is not None:
                old_parent.remove_child(self)
            if new_parent is not None:
                new_parent.add_child(self)

    # =========================
    def add_child(self, child):
        """
        This method is designed to add a child node to this node

        :type child: HierarchicalNode
        :param child: The child node to add to this node
        """
        if child.get_parent() is self:
            child_category = child.get_node_category()
            try:
                named_sequence = self.__children_dict[child_category]
            except KeyError:
                named_sequence = NamedSequence([child], "get_name")
                self.__children_dict[child_category] = named_sequence
            else:
                named_sequence.append(child)
        else:
            child.set_parent(self)

    # ============================
    def remove_child(self, child):
        """
        This method is designed to remove a child node from this node

        :type child: HierarchicalNode
        :param child: the child node to remove from this node
        """
        child_category = child.get_node_category()
        named_sequence = self.__children_dict[child_category]
        named_sequence.remove(child)

    # ============================
    def get_data(self, data_name):
        """
        This method is designed to get a data from this node

        :type data_name: str
        :param data_name: the name of the data to get

        :rtype: any
        :return: the desired data
        """
        return self.__data_dict[data_name]

    # ===================================
    def set_data(self, data_name, value):
        """
        This method is designed to update or set a data of this node

        :type data_name: str
        :param data_name: the name of the data to update

        :type value: any
        :param value: the data to update or set
        """
        self.__data_dict[data_name] = value

    # ================================
    def get_data_names_iterator(self):
        """
        This method is designed to get an iterator over the names of the data of this node

        :rtype: Generator[str]
        :return: an iterator over the names of the data of this node
        """
        for elem in self.__data_dict:
            yield elem

    # =======================
    def get_data_names(self):
        """
        This method is designed to get the list of the names of the data of this node

        :rtype: list[str]
        :return: the list of the names of the data of this node
        """
        return [elem for elem in self.get_data_names_iterator()]

    # ===============================
    def remove_data(self, data_name):
        """
        This method is designed to remove a data from this node

        :type data_name: str
        :param data_name: the name of the data to remove
        """
        del self.__data_dict[data_name]

    # ======================
    def get_data_dict(self):
        """
        This method is designed to get the dictionnary of the data of the node
        Warning : Modifying the returned dictionnary won't modiy the dictionnary of the instance, yet modifying the data itself will

        :rtype: dict[str, any]
        :return: the dictionnary of the data of the node
        """
        res = {elem: self.__data_dict[elem] for elem in self.__data_dict}
        return res

    # =================================================
    def get_nb_child_in_category(self, child_category):
        """
        This method is designed to get the number of children within a category for this node

        :type child_category: str
        :param child_category: the inspected category

        :rtype: int
        :return: the number of children within the indicated category for this node
        """
        try:
            named_sequence = self.__children_dict[child_category]
        except KeyError:
            msg = "The required category '%s' does not exist !" % child_category
            raise HierarchicalNodeMismatchException(msg)

        return len(named_sequence)

    # ===========================================
    def get_child(self, child_category, pointer):
        """
        This method is designed to get a child node of this node

        :type child_category: str
        :param child_category: the category of the desired child

        :type pointer: int | str
        :param pointer: name or index of the child in the category

        :rtype: HierarchicalNode
        :return: the desired child node
        """
        try:
            named_sequence = self.__children_dict[child_category]
        except KeyError:
            msg = "The required category '%s' does not exist !" % child_category
            raise HierarchicalNodeMismatchException(msg)
        else:
            try:
                child = named_sequence[pointer]
            except (KeyError, IndexError):
                if isinstance(pointer, int):
                    msg = "No child node at index %i for the category '%s' !"
                else:
                    msg = "No child node name '%s' for the category '%s' !"
                msg %= (pointer, child_category)
                raise HierarchicalNodeMismatchException(msg)

        return child

    # ==========================================================
    def get_children_in_category_iterator(self, child_category):
        """
        This method is designed to get an iterator over the children within a category for this node

        :type child_category: str
        :param child_category: the inspected category

        :rtype: Generator[HierarchicalNode]
        :return: an iterator over the children within the desired category for this node
        """
        try:
            named_sequence = self.__children_dict[child_category]
        except KeyError:
            pass
        else:
            for elem in named_sequence:
                yield elem

    # =================================================
    def get_children_in_category(self, child_category):
        """
        This method is designed to get the NamedSequence of children within a category for this node
        Warning : modifying the result NamedSequence won't moddify this instance, yet modifying the contained nodes will

        :type child_category: str
        :param child_category: the inspected category

        :rtype: NamedSequence[HierarchicalNode]
        :return: the NamedSequence of children within the desired category for this node
        """
        return self.__children_dict[child_category].copy()

    # ========================================================
    def get_sorted_children_in_category(self, child_category):
        """
        This method is designed to get the NamedSequence of children within a category for this node, ordered by name
        Warning : modifying the result NamedSequence won't moddify this instance, yet modifying the contained nodes will

        :type child_category: str
        :param child_category: the inspected category

        :rtype: NamedSequence[HierarchicalNode]
        :return: the NamedSequence of children within the desired category for this node, ordered by name
        """
        res = self.get_children_in_category(child_category)
        res.sort()

        return res

    # ================================
    def get_categories_iterator(self):
        """
        This method is designed to get an iterator over the categories of this node

        :rtype: Generator[str]
        :return: an iterator over the categories of this node
        """
        for category in self.__children_dict:
            yield category

    # =======================
    def get_categories(self):
        """
        This method is designed to get the list of categories of this node

        :rtype: list[str]
        :return: the list of categories of this node
        """
        return [category for category in self.get_categories_iterator()]

    # ==============================
    def get_sorted_categories(self):
        """
        This method is designed to get the list of categories of this node ordered by name

        :rtype: list[str]
        :return: the list of categories of this node ordered by name
        """
        return sorted(self.get_categories_iterator())

    # =========================================================
    def walk_for_data(self, category, complementary_data=None):
        """
        This method is designed to walk the data until the indicated categoy is reached and returns the data
        of the matching nodes

        :type category: str
        :param category: the aimed category

        :type complementary_data: dict|None
        :param complementary_data: parent node data used to complete child node data (Used in recursion)

        :rtype: list[dict]
        :return: liste of type [{"data": data_dict, "name": <node_name>: "node": node}]
        """
        res = []
        if complementary_data is None:
            complementary_data = {}
        try:
            child_iterator = self.get_sorted_children_in_category(category)
        except Exception:
            my_data = self.get_data_dict()
            for category in self.get_sorted_categories():
                for child in self.get_sorted_children_in_category(category):
                    res += child.walk_for_data(category, complementary_data=my_data)
        else:
            for child in child_iterator:
                child_name = child.get_name()
                data = child.get_data_dict()
                data.update(complementary_data)
                res.append({"data": data, "name": child_name, "node": child})

        return res

    # ================
    def __str__(self):
        """
        Overloaded __str__ method to view the hierarchical structure

        :rtype: str
        :return: str depicting the hierarchical structure
        """
        s = self.__name
        for category in self.get_sorted_categories():
            s = s + '\n .  \n ...CATEGORIE: ' + category
            for child in self.get_sorted_children_in_category(category):
                child_str = child.__str__().replace('\n', '\n        ')
                s = s + '\n     .  \n     ...' + child_str

        return s


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
