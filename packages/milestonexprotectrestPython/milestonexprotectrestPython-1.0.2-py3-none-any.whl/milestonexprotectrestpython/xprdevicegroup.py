"""
Module: xprdevicegroup.py

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
class XPRDeviceGroup:
    """
    Device Group information.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fBuiltIn:bool = False
        self._fDateModified:datetime = None
        self._fDescription:str = None
        self._fDisplayName:str = None
        self._fId:str = None
        self._fItemType:str = None
        self._fName:str = None


    @property
    def BuiltIn(self) -> bool:
        """ 
        The BuiltIn status of the group - True if BuiltIn; otherwise False.

        Returns:
            The BuiltIn property value.
        """
        return self._fBuiltIn

    @BuiltIn.setter
    def BuiltIn(self, value:bool) -> None:
        """ 
        Sets the BuiltIn property value.
        """
        if value != None:
            self._fBuiltIn = value


    @property
    def DateModified(self) -> datetime:
        """ 
        Date and time (in UTC format) that the group entry was last modified.

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
    def Description(self) -> str:
        """ 
        A description of the group.

        Returns:
            The Description property value.
        """
        return self._fDescription

    @Description.setter
    def Description(self, value:str) -> None:
        """ 
        Sets the Description property value.
        """
        self._fDescription = value


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
    def ItemType(self) -> str:
        """ 
        Type of the group item.

        Returns:
            The ItemType property value.
        """
        return self._fItemType

    @ItemType.setter
    def ItemType(self, value:str) -> None:
        """ 
        Sets the ItemType property value.
        """
        self._fItemType = value


    @property
    def Name(self) -> str:
        """ 
        Name of the group.

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


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "Name - Description"
        """
        return str.format("{0} - {1}", self.Name or "", self.Description or "")


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception as ex:
            if (isinstance(self, XPRDeviceGroup)) and (isinstance(other, XPRDeviceGroup)):
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
            if (isinstance(self, XPRDeviceGroup)) and (isinstance(other, XPRDeviceGroup)):
                return self.Name < other.Name
            return False
