"""
Module: xprenumcomparable.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/07/11 | 1.0.0.0     | Initial Version.  

</details>
"""

from enum import Enum
import numbers

class XPREnumComparable(Enum):
    """
    Class used to compare Enum objects without having to specify ".value" on
    the end of the enum name.
    """

    def __init__(self, other) -> None:
        """
        Initializes a new instalce of the class.

        Args:
            other (object):
                Object to compare with this object.
        """
        pass


    def __gt__(self, other):
        """
        Compares if the other object is greater than the current object.

        Args:
            other (object):
                Object to compare with this object.
        """
        try:
            return self.value > other.value     # try to compare the values first.
        except:
            pass
        try:
            if isinstance(other, numbers.Real): # try to compare the values first.
                return self.value > other
        except:
            pass
        return NotImplemented


    def __lt__(self, other):
        """
        Compares if the other object is less than the current object.

        Args:
            other (object):
                Object to compare with this object.
        """
        try:
            return self.value < other.value
        except:
            pass
        try:
            if isinstance(other, numbers.Real):
                return self.value < other
        except:
            pass
        return NotImplemented


    def __ge__(self, other):
        """
        Compares if the other object is greater than or equal to the current object.

        Args:
            other (object):
                Object to compare with this object.
        """
        try:
            return self.value >= other.value
        except:
            pass
        try:
            if isinstance(other, numbers.Real):
                return self.value >= other
            if isinstance(other, str):
                return self.name == other
        except:
            pass
        return NotImplemented


    def __le__(self, other):
        """
        Compares if the other object is less than or equal to the current object.

        Args:
            other (object):
                Object to compare with this object.
        """
        try:
            return self.value <= other.value
        except:
            pass
        try:
            if isinstance(other, numbers.Real):
                return self.value <= other
            if isinstance(other, str):
                return self.name == other
        except:
            pass
        return NotImplemented


    def __eq__(self, other):
        """
        Compares if the other object is equal to the current object.

        Args:
            other (object):
                Object to compare with this object.
        """
        if (other == None):
            return False

        try:
            return self.value == other.value
        except:
            pass

        try:
            if isinstance(other, numbers.Real):
                return self.value == other
            if isinstance(other, str):
                return self.name == other
        except:
            pass

        return NotImplemented
