"""
Module: xprfilteroperator.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/05/30 | 3.0.0.0     | Initial Version.  

</details>
"""


# our package imports.
from .xprenumcomparable import XPREnumComparable

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPRFilterOperator(XPREnumComparable):
    """
    Filter Types.
    """

    NotSet = 0
    """
    Filter type will not be used.
    """

    lt = 1
    """
    Less Than operator.  
    Used to evaluate numerical and date or time property values.
    """

    gt = 2
    """
    Greater Than operator.  
    Used to evaluate numerical and date or time property values.
    """

    equals = 3
    """
    Equals operator.  
    Used to match a string property value that exactly matches a specified value.
    """

    notEquals = 4
    """
    Not equals operator.  
    Used to match a string property value that does not match a specified value.
    """

    startsWith = 5
    """
    String starts with operator.  
    Used to match a string property value that begins with a specified value.
    """

    contains = 6
    """
    String that contains operator.  
    Used to match a string property value that contains a specified value.
    """
