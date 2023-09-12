# coding=utf-8
"""
This module contains the class NamedSequence
"""
from __future__ import annotations
from . import __author__ , __email__, __version__ , __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from typing import TypeVar, List, Iterable


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================
T = TypeVar('T')


# ==================================================================================================
# CLASSES
# ==================================================================================================

# ============================
class NamedSequence(List[T]):
    """
    This class represents sequence of named objects.
    Each object of the sequence shall have method with a common name to get the name of the object

    The __getitem__ and setitem__ now allow str instead of int, the string being the name of the desired object


    Instance attributes:
    :type __get_name_method_name: str
    :ivar __get_name_method_name: the name of the method to get the name of each object of the sequence
    """
    # =================================================
    def __init__(self, sequence, get_name_method_name):
        """
        Initialization of a NamedSequence instance

        :type sequence: Iterable
        :param sequence: the sequence of named objects that must be converted to NamedSequence

        :type get_name_method_name: str
        :param get_name_method_name: the name of the method to get the name of the objects of the Sequence
        """
        super().__init__(sequence)
        self.__get_name_method_name = get_name_method_name

    # ========================
    def __get_idx(self, name):
        """
        This method is designed to get the position of the first object of the list based on its name

        :type name: str
        :param name: the name of the desired object

        :rtype: int
        :return: the position of the first object of the list based on its name
        """
        idx = -1
        for i, item in enumerate(self):
            get_name_method = getattr(item, self.__get_name_method_name)
            test_name = get_name_method()
            if name == test_name:
                idx = i
                break

        if idx == -1:
            raise KeyError(f"No item named '{name}' !")

        return idx

    # =============================
    def index(self, item: T | str):
        """
        This method is designed to get the index of an item of this instance

        :type item: str | any
        :param item: item or name of an item

        :rtype: int
        :return: the index of the designed item of this instance
        """
        if isinstance(item, str):
            res = self.__get_idx(item)
        else:
            res = super().index(item)

        return res

    # ====================================
    def __contains__(self, item: T | str):
        """
        This method is designed to check if the instance contains an item

        :type item: str | any
        :param item: item or name of an item

        :rtype: bool
        :return: True if the instance contains the item or an item of the given name, False otherwise.
        """
        if isinstance(item, str):
            try:
                self.__get_idx(item)
            except KeyError:
                res = False
            else:
                res = True
        else:
            res = super().__contains__(item)

        return res

    # =====================================================
    def __getitem__(self, pointer) -> T | NamedSequence[T]:
        """
        This method is designed to get an item or slice of items from this instance

        :type pointer: int | str | slice
        :param pointer: pointer to a named object of the instance or a slice of objects

        :rtype: any | NamedSequence
        :return: the item or slice of items
        """
        if isinstance(pointer, str):
            pointer = self.__get_idx(pointer)

        res = super().__getitem__(pointer)
        if isinstance(pointer, slice):
            res = NamedSequence(res, self.__get_name_method_name)

        return res

    # =====================================================
    def __setitem__(self, pointer, value: T | Iterable[T]):
        """
        This method is designed to set an item or slice of item of this instance

        :type pointer: int | str | slice
        :param pointer: pointer to a named object of the instance or a slice of objects

        :type value: any | Iterable
        :param value: item to add or iterable of item if pointer is a slice
        """
        if isinstance(pointer, str):
            pointer = self.__get_idx(pointer)

        super().__setitem__(pointer, value)

    # ==================================
    def insert(self, pointer, value: T):
        """
        This method is designed to insert an item at a given position

        :type pointer: str | int
        :param pointer: position of insertion or name of an item where the insertion will occur

        :type value: any
        :param value: the item to insert
        """
        if isinstance(pointer, str):
            try:
                pointer = self.__get_idx(pointer)
            except KeyError:
                pointer = len(self)

        super().insert(pointer, value)

    # =============================
    def pop(self, pointer=-1) -> T:
        """
        This method is designed to get and remove an item

        :type pointer: int | str
        :param pointer: position or name of the item to remove

        :rtype: any
        :return: the removed item
        """
        if isinstance(pointer, str):
            pointer = self.__get_idx(pointer)

        return super().pop(pointer)

    # =============================
    def __delitem__(self, pointer):
        """
        This method is designed to remove an item at of this instance

        :type pointer: str | int
        :param pointer: position of removal or name of the item to remove
        """
        if isinstance(pointer, str):
            pointer = self.__get_idx(pointer)

        super().__delitem__(pointer)

    # =================================
    def remove(self, pointer: T | str):
        """
        This method is designed to remove an item from this instance

        :type pointer: any | str
        :param pointer: the item or name of the item to remove
        """
        if isinstance(pointer, str):
            pointer = self.__get_idx(pointer)
            self.__delitem__(pointer)
        else:
            super().remove(pointer)

    # =============================================================
    def __add__(self, other: NamedSequence[T]) -> NamedSequence[T]:
        """
        Overloaded __add__ method to return a NamedSequence

        :type other: NamedSequence
        :param other: the other sequence to add

        :rtype: NamedSequence
        :return: the concatenation of the two sequences
        """
        if not isinstance(other, NamedSequence):
            raise TypeError("Unable to use the __add__ operator with a non NamedSequence instance !")

        if self.__get_name_method_name != other.__get_name_method_name:
            raise Exception("Unable to use the __add__ operator when the name of the method to get the objects name is different !")

        res = super().__add__(other)

        return NamedSequence(res, self.__get_name_method_name)

    # =============================================================
    def __iadd__(self, other: NamedSequence[T], from_extend=False):
        """
        Overloaded __iadd__ method to return a NamedSequence

        :type other: NamedSequence
        :param other: the other sequence to add

        :type from_extend: bool
        :param from_extend: True if the method is called from the extend method (it changes error messages)

        :rtype: NamedSequence
        :return: the concatenation of the two sequences
        """
        if not isinstance(other, NamedSequence):
            if from_extend:
                msg = "Unable to use the extend method with a non NamedSequence instance !"
            else:
                msg = "Unable to use the __iadd__ operator with a non NamedSequence instance !"
            raise TypeError(msg)

        if self.__get_name_method_name != other.__get_name_method_name:
            if from_extend:
                msg = "Unable to use the extend method when the name of the method to get the objects name is different !"
            else:
                msg = "Unable to use the __iadd__ operator when the name of the method to get the objects name is different !"
            raise Exception(msg)

        return super().__iadd__(other)

    # ========================================
    def extend(self, other: NamedSequence[T]):
        """
        Overloaded extend method identical to __iadd__ except there is no return

        :type other: NamedSequence
        :param other: the other sequence to add
        """
        self.__iadd__(other, from_extend=True)

    # ===========================================
    def __mul__(self, other) -> NamedSequence[T]:
        """
        This method is designed to multiply the content of this instance

        :type other: int
        :param other: the multiplier

        :rtype: NamedSequence
        :return: the multiplied sequence
        """
        res = super().__mul__(other)

        return NamedSequence(res, self.__get_name_method_name)

    # ============================================
    def __rmul__(self, other) -> NamedSequence[T]:
        """
        This method is designed to multiply (by the left) the content of this instance

        :type other: int
        :param other: the multiplier

        :rtype: NamedSequence
        :return: the multiplied sequence
        """
        return self.__mul__(other)

    # ======================
    def __eq__(self, other):
        """
        This method is designed to chekc if the content of this instance is similar to another

        :type other: any
        :param other: the other instance

        :rtype: bool
        :return: True if the content of the two instances are similar, False otherwise.
        """
        res = isinstance(other, NamedSequence)
        if res:
            res = self.__get_name_method_name == other.__get_name_method_name
            res &= super().__eq__(other)

        return res

    # =================================
    def copy(self) -> NamedSequence[T]:
        """
        This method is designed to get a copy of this instance

        :rtype: NamedSequence
        :return: a copy of this instance
        """
        return NamedSequence(self, self.__get_name_method_name)

    # ===============================
    def count(self, pointer: T | str):
        """
        This method is designed to get the number of time an object is present in this instance

        :type pointer: any | str
        :param pointer: the counted object or its name

        :rtype: int
        :return: the number of time the object is present in this instance
        """
        if isinstance(pointer, str):
            res = 0
            for elem in self:
                res += int(elem.get_name() == pointer)
        else:
            res = super().count(pointer)

        return res

    # ======================================
    def sort(self, key=None, reverse=False):
        """
        This method is designed to sort the content of this instance

        :type key: NoneType | Callable
        :param key: standard "key" argument of the sort method of a list

        :type reverse: bool
        :param reverse: True to reverse the sort, False otherwise
        """
        if key is None:
            try:
                super().sort(key=key, reverse=reverse)
            except TypeError:
                key = lambda x: getattr(x, self.__get_name_method_name)()

        if key is not None:
            super().sort(key=key, reverse=reverse)

    # =================
    def __repr__(self):
        """
        Overloaded __repr__ method to get a string representation of this instance

        :rtype: str
        :return: a string representation of this instance
        """
        return "%s(%s, %s)" % (self.__class__.__name__, super().__repr__(), self.__get_name_method_name)


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
