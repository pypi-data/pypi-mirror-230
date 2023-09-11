"""
Module: xprcollection.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/07/11 | 1.0.0.0     | Initial Version.  

</details>
"""

import _threading_local
from typing import Iterable

# our package imports.
from .xprappmessages import XPRAppMessages

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export

@export
class XPRCollection(Iterable):
    """ 
    Collection of objects.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self, itemType:type=None) -> None:
        """
        Initializes a new instance of the class.

        Args:
            itemType (type):
                Type of items this collection will contain.                                    
        """
        # validations.
        if (itemType == None):
            raise Exception(XPRAppMessages.ARGUMENT_REQUIRED_ERROR.format("itemType"))
        if (not isinstance(itemType, type)):
            raise Exception(XPRAppMessages.ARGUMENT_TYPE_ERROR.format("itemType", "type", type(itemType).__name__))
        
        # initialize class instance.
        self._fLock = _threading_local.RLock()
        self._fItems = list()
        self._fItemType:type = itemType        


    def append(self, item) -> None:
        """
        Adds a new item to the collection.

        Args:
            item (object):
                Item that will be added to the collection.

        Raises:
            TypeError:
                Item argument is not of a type specified when the collection was initialized.
        """
        with self._fLock:

            if (item != None):

                self._ValidateItemType(item, "append", "item")
                self._fItems.append(item)


    @property
    def count(self) -> int:
        """
        Returns the number of items in the collection.

        Returns:
            The number of items in the collection.
        """
        with self._fLock:

            return len(self._fItems)


    def clear(self) -> None:
        """
        Removes all items in the collection.
        """
        with self._fLock:

            self._fItems.clear()


    def extend(self, other:object) -> None:
        """
        Extends the collection with items from another collection.

        Args:
            other (object):
                Collection of items to add to the collection.

        """
        with self._fLock:

            if isinstance(other, type(self)):
                self._fItems.extend(other)
            else:
                self._fItems.extend(self._ValidateItemType(item, "extend", "other") for item in other)


    def get(self, index:int) -> object:
        """
        Read an item from the collection at the specified index.

        Args:
            index (int):
                Index of the collection item to get.

        Returns:
            The collection item at the specified index.
        """
        with self._fLock:

            return self._fItems[index]
 

    def insert(self, index:int, item:object) -> None:
        """
        Inserts a new item in the collection at the specified index.

        Args:
            index (int):
                Index at which to insert the new item.
            item (object):
                Item that will be added to the collection.

        Raises:
            TypeError:
                Item argument is not of a type specified when the collection was initialized.
        """
        with self._fLock:

            if (item != None):

                self._ValidateItemType(item, "insert", "item")

                # validation - avoid index out of range exception.
                if (index < 0):
                    index = 0
                if (index >= len(self._fItems)):
                    index = len(self._fItems)

                self._fItems.insert(index, item)


    @property
    def length(self) -> int:
        """
        Returns the number of items in the collection.

        Returns:
            The number of items in the collection.
        """
        with self._fLock:

            return len(self._fItems)


    def pop(self) -> object:
        """
        Remove and return the last item from the collection.

        Returns:
            The last item from the collection.
        """
        with self._fLock:

            return self._fItems.pop()
 

    def remove(self, item:object) -> None:
        """
        Removes an item from the collection.

        Args:
            item (object):
                Item that will be removed from the collection.

        Raises:
            TypeError:
                Item argument is not of a type specified when the collection was initialized.
        """
        with self._fLock:

            if (item != None):

                self._ValidateItemType(item, "remove", "item")

                for colitem in self._fItems:
                    if (colitem is item):
                        self._fItems.remove(item)
                        return

 
    def sort(self, **kwargs) -> None:
        """
        Sorts the collection items by Name (default).

        Use the following guidelines when calling a sort method that uses key=lambda syntax:
        ```
        # good syntax, as it handles x.Name = None values.
        epColl.sort(key=lambda x: x.Name or "", reverse=False)

        # bad syntax, as the sort will fail if x.Name = None!
        epColl.sort(key=lambda x: x.Name, reverse=False)
        ```
        """
        with self._fLock:

            self._fItems.sort(**kwargs)
 

    def _ValidateItemType(self, item:object, methodName:str, argumentName:str) -> None:
        """
        Validates that the item being added / updated is of a type specified when the
        collection was constructed.

        Args:
            item (object):
                Item object to validate.
            methodName (str):
                Method name that called this validation routine; used for exception message details.
            argumentName (str):
                Argument name of the method that called this validation routine; used for exception message details.

        Raises:
            TypeError:
                Item argument is not of a type specified when the collection was initialized.
        """
        with self._fLock:

            # is item type the same as the desired item type?  if so, then we are done.
            if isinstance(item, self._fItemType):
                return item

            # otherwise, we cannot process this type of item.
            raise TypeError(XPRAppMessages.COLLECTION_ARGUMENT_TYPE_ERROR.format(methodName, argumentName, self._fItemType.__name__, type(item).__name__))


    # public interface methods.

    def __iter__(self) -> iter:
        """
        Implement Iterator interface method in a thread-safe manner.
        """
        with self._fLock:

            return iter(self._fItems)


    def __len__(self) -> int:
        """
        Implement len interface method in a thread-safe manner.
        """
        with self._fLock:

            return len(self._fItems)


    def __setitem__(self, index:int, item:object) -> None:
        """
        Updates the collection item at the specified index.

        Args:
            item (object):
                Item that will be added to the collection.

        Raises:
            TypeError:
                Item argument is not of a type specified when the collection was initialized.
        """
        with self._fLock:

            if (item != None):

                self._ValidateItemType(item, "__setitem__", "item")

                # validation - avoid index out of range exception.
                if (index < 0):
                    index = 0
                if (index >= len(self._fItems)):
                    index = len(self._fItems)

                self._fItems.__setitem__(index, self._ValidateItemType(item))


    def __getitem__(self, index:int) -> object:
        """
        Reads an item from the collection at the specified index.

        Args:
            index (int):
                Index of the collection item to get.

        Returns:
            The collection item at the specified index.
        """
        with self._fLock:

            # validation - avoid index out of range exception.
            if (index < 0):
                index = 0
            if (index >= len(self._fItems)):
                index = len(self._fItems)

            return self._fItems.__getitem__(index)


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string representation of each item in the collection, delimited by CRLF characters.
        """
        with self._fLock:

            value:str = ""

            for item in self._fItems:
                value += str(item) + "\r\n"

            # drop ending delimiter.
            valueLen:int = len(value)
            if (valueLen > 2):
                value = value[0:valueLen-2]

            return value
