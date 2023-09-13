# coding=utf-8
"""
This module contains the class TptNode
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
from typing import TextIO, Generator
from protected_method_metaclass import Protected
from hierarchical_storage import HierarchicalNodeMismatchException
from tpt_reading.base_node import BaseNode
from tpt_reading import TptNodeMismatchException


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ======================
class TptNode(BaseNode):
    """
    This class defines a Node from a template file
    TptNode instances are defined by tags in template files

    Instance attributes:
    :type __node_type: str
    :ivar __node_type: string describing the type of node (usually taken from the tag name in template file)

    :type __node_args: list[str]
    :ivar __node_args: list of special arguments for the node (usually taken from the tags  in template file)

    :type __parent: NoneType | TptNode
    :ivar __parent: Le TptNode parent of this instance (None if not parent)

    :type __children: list[TptNode]
    :ivar __children: list of child TptNodes of this instance
    """

    # ====================================================
    def __init__(self, node_type, node_args, parent=None):
        """
        Initialization of a TptNode instance

        :type node_type: str
        :param node_type: string describing the type of node (usually taken from the tag name in template file)

        :type node_args: list[str]
        :param node_args: list of special arguments for the noe liste des arguments speciaux du noeud (usually taken from the tags  in
                          template file)

        :type parent: NoneType | TptNode
        :param parent: list of child TptNodes of this instance
        """
        self.__node_type = node_type
        self.__node_args = node_args
        self.__parent = parent
        self.__children = []
        if parent is not None:
            parent.add_child(self)

    # ======================
    def get_node_type(self):
        """
        This method is designed to get the string describing the type of node

        :rtype: str
        :return: the string describing the type of node
        """
        return self.__node_type

    # ======================
    def get_node_args(self):
        """
        This method is designed to get the list of special arguments for the node

        :rtype: list[str]
        :return: the list of special arguments for the node
        """
        res = [elem for elem in self.__node_args]
        return res

    # =========================
    def add_child(self, child):
        """
        This method is designed to add a child node to this node

        :type child: TptNode
        :param child: the child node to add
        """
        self.__children.append(child)

    # ===================
    def get_parent(self):
        """
        This method is designed to get the parent node of this node

        :rtype: NoneType | TptNode
        :return: the parent node of this node
        """
        return self.__parent

    # =====================
    def get_nb_child(self):
        """
        This method is designed to get the number of children of this node

        :rtype: int
        :return: the number of children of this node
        """
        return len(self.__children)

    # =============================
    def get_child_idx(self, child):
        """
        This method is designed to get the index of the child

        :type child: TptNode
        :param child: the child whose index is desired

        :rtype: int
        :return: the index of the child
        """
        try:
            rvalue = self.__children.index(child)
        except ValueError:
            msg = "The requested child TptNode does not exist !"
            raise TptNodeMismatchException(msg)

        return rvalue

    # ==========================
    def get_child_at(self, idx):
        """
        This method is designed to get a child of this node

        :type idx: int
        :param idx: the index of the child node

        :rtype: TptNode
        :return: the child node at the indicated index
        """
        try:
            child = self.__children[idx]
        except IndexError:
            msg = "No TptNode at the given index !"
            raise TptNodeMismatchException(msg)

        return child

    # =================
    def __iter__(self):
        """
        This method is designed to get an iterator over the children of this node

        :rtype: Generator[TptNode]
        :return: an iterator over the children of this node
        """
        for child in self.__children:
            yield child

    # ================
    def __str__(self):
        """
        Overloaded __str__ method to visualize the structure of the node

        :rtype: str
        :return: the structure of the node
        """
        s = self.__node_type
        for child in self.__children:
            child_str = child.__str__().replace('\n', '\n    ')
            s = s + '\n .  \n ...' + child_str

        return s

    # ========
    @Protected
    def __read_bloc(self, bloc_name, bloc_args, f, parent_node):
        """
        This method is designed to read a block and add the node of the bloc to its parent node

        :type bloc_name: str
        :param bloc_name: Te name of the created bloc

        :type bloc_args: list[str]
        :param bloc_args: list of additional arguments for the node to create

        :type f: TextIO
        :param f: The file being read

        :type parent_node: TptNode
        :param parent_node: parent node of the created node

        :rtype: str
        :return: The last read line (just after the end of the block)
        """
        factory = self.get_factory()

        cur_node = TptNode(bloc_name, bloc_args, parent_node)
        data = ''
        end_tag = "[/{0}]".format(bloc_name)
        line = f.readline()
        strip_line = line.strip()
        while strip_line != end_tag:
            if strip_line.startswith("[BLOC"):
                if data != '':
                    factory.get_instance_from_id("TptDataNode", cur_node, data)
                    # TptDataNode(cur_node, data)
                    data = ''
                bloc_tag = strip_line[1:-1]
                test_splits = bloc_tag.split(" ")
                bloc_name = test_splits[0]
                new_bloc_args = test_splits[1:]
                line = self.__read_bloc(bloc_name, new_bloc_args, f, cur_node)
                strip_line = line.strip()
            else:
                data += line
                line = f.readline()
                strip_line = line.strip()
        if data != '':
            factory.get_instance_from_id("TptDataNode", cur_node, data)
            # TptDataNode(cur_node, data)
        line = f.readline()
        return line

    # ======================================
    def get_text(self, data_dict, ref_item):
        """
        This method is designed to get the text of the node updated with the data

        :type data_dict: dict[str: str]
        :param data_dict: dictionnary with complementary data

        :type ref_item: HierarchicalNode
        :param ref_item: the HierarchicalNode containing the data

        :rtype: str
        :return: the text of the node updated with the data
        """
        s = ''
        test_splits = self.__node_type.split('_')
        if len(test_splits) > 2:
            tpt_node_cat = test_splits[1]
            hierarchical_node_cat = '_'.join(test_splits[2:])
            if tpt_node_cat == "IF":
                try:
                    ref_item.get_nb_child_in_category(hierarchical_node_cat)
                except HierarchicalNodeMismatchException:
                    pass
                else:
                    for child in self.__children:
                        s += child.get_text(data_dict, ref_item)
            elif tpt_node_cat == "FOR":
                for func_res in ref_item.walk_for_data(hierarchical_node_cat):
                    new_data_dict = func_res["data"]
                    new_item = func_res["node"]
                    s2 = ""
                    for child in self.__children:
                        s2 += child.get_text(new_data_dict, new_item)
                    if "NO_JUMP" in self.__node_args:
                        s += s2[0:-1]
                    else:
                        s += s2
                if "NO_JUMP" in self.__node_args and "NO_END_JUMP" not in self.__node_args:
                    s += '\n'
            else:
                for child in self.__children:
                    s += child.get_text(data_dict, ref_item)
        else:
            s2 = ''
            for child in self.__children:
                s2 += child.get_text(data_dict, ref_item)
            if "NO_END_JUMP" in self.__node_args:
                s += s2[0:-1]
            else:
                s += s2

        for key in data_dict:
            s = s.replace("@" + key + "@", data_dict[key])

        return s

    # ==============================
    def get_example_text(self):
        """
        This method is designed to get the text of the node

        :rtype: str
        :return: the text of the node
        """
        s = ''
        test_splits = self.__node_type.split('_')
        if len(test_splits) > 2:
            tpt_node_cat = test_splits[1]
            if tpt_node_cat == "IF":
                for child in self.__children:
                    s += child.get_example_text()
            elif tpt_node_cat == "FOR":
                for _ in range(2):
                    s2 = ""
                    for child in self.__children:
                        s2 += child.get_example_text()
                    if "NO_JUMP" in self.__node_args:
                        s += s2[0:-1]
                    else:
                        s += s2
                if "NO_JUMP" in self.__node_args and "NO_END_JUMP" not in self.__node_args:
                    s += '\n'
            else:
                for child in self.__children:
                    s += child.get_example_text()
        else:
            s2 = ''
            for child in self.__children:
                s2 += child.get_example_text()
            if "NO_END_JUMP" in self.__node_args:
                s += s2[0:-1]
            else:
                s += s2

        return s


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
