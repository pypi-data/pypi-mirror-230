"""
Module: xpreventtypegroup.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/07/11 | 1.0.0.0     | Initial Version.  

</details>
"""


# external package imports.
from datetime import datetime

# our package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPREventTypeGroup:
    """
    Event Type Group information.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fDisplayName:str = None
        self._fId:str = None


    @property
    def DisplayName(self) -> str:
        """ 
        User-friendly display name used in various user-interface displays.

        Returns:
            The DisplayName property value.
        """
        return self._fDisplayName

    @DisplayName.setter
    def DisplayName(self, value:str) -> None:
        """ 
        Sets the DisplayName property value.
        """
        self._fDisplayName = value


    @property
    def Id(self) -> str:
        """ 
        The globally unique identifier of the item.

        Returns:
            The Id property value.
        """
        return self._fId

    @Id.setter
    def Id(self, value:str) -> None:
        """ 
        Sets the Id property value.
        """
        self._fId = value


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "DisplayName - Id"
        """
        return str.format("{0} - {1}", self.DisplayName or "", self.Id or "")


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.DisplayName == other.DisplayName
        except Exception as ex:
            if (isinstance(self, XPREventTypeGroup )) and (isinstance(other, XPREventTypeGroup )):
                return self.DisplayName == other.DisplayName
            return False

    def __lt__(self, other):
        try:
            # the following comparison will fail if the property value is None!  
            # use the following syntax when calling a sort method that uses lambda searches:
            # epColl.sort(DisplayName=lambda x: x.DisplayName or "", reverse=False)     <- GOOD syntax
            # epColl.sort(DisplayName=lambda x: x.DisplayName, reverse=False)           <- BAD syntax, as the "x.DisplayName" property may be None, and will cause this to fail!
            return self.DisplayName < other.DisplayName
        except Exception as ex:
            if (isinstance(self, XPREventTypeGroup )) and (isinstance(other, XPREventTypeGroup )):
                return self.DisplayName < other.DisplayName
            return False
