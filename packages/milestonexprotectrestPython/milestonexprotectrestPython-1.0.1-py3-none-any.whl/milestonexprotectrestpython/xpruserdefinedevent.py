"""
Module: xpruserdefinedevent.py

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
class XPRUserDefinedEvent:
    """
    User Defined Event information.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fDateCreated:datetime = None
        self._fDateModified:datetime = None
        self._fDisplayName:str = None
        self._fId:str = None
        self._fName:str = None
        self._fSubType:str = None

        
    @property
    def DateCreated(self) -> datetime:
        """ 
        Date and time (in UTC format) that the entry was created.

        Returns:
            The DateCreated property value.
        """
        return self._fDateCreated

    @DateCreated.setter
    def DateCreated(self, value:datetime) -> None:
        """ 
        Sets the DateCreated property value.
        """
        self._fDateCreated = value


    @property
    def DateModified(self) -> datetime:
        """ 
        Date and time (in UTC format) that the entry was last modified.

        Returns:
            The DateModified property value.
        """
        return self._fDateModified

    @DateModified.setter
    def DateModified(self, value:datetime) -> None:
        """ 
        Sets the DateModified property value.
        """
        self._fDateModified = value


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
        The globally unique identifier of the group.

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


    @property
    def Name(self) -> str:
        """ 
        Name of the event.

        Returns:
            The Name property value.
        """
        return self._fName

    @Name.setter
    def Name(self, value:str) -> None:
        """ 
        Sets the Name property value.
        """
        self._fName = value


    @property
    def SubType(self) -> str:
        """ 
        SubType of the event.

        Returns:
            The SubType property value.
        """
        return self._fSubType

    @SubType.setter
    def SubType(self, value:str) -> None:
        """ 
        Sets the SubType property value.
        """
        self._fSubType = value


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "Name - Id"
        """
        return str.format("{0} - {1}", self.Name or "", self.Id or "")


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception as ex:
            if (isinstance(self, XPRUserDefinedEvent )) and (isinstance(other, XPRUserDefinedEvent )):
                return self.Name == other.Name
            return False

    def __lt__(self, other):
        try:
            # the following comparison will fail if the property value is None!  
            # use the following syntax when calling a sort method that uses lambda searches:
            # epColl.sort(Name=lambda x: x.Name or "", reverse=False)     <- GOOD syntax
            # epColl.sort(Name=lambda x: x.Name, reverse=False)           <- BAD syntax, as the "x.Name" property may be None, and will cause this to fail!
            return self.Name < other.Name
        except Exception as ex:
            if (isinstance(self, XPRUserDefinedEvent )) and (isinstance(other, XPRUserDefinedEvent )):
                return self.Name < other.Name
            return False
