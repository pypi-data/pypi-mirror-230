"""
Module: xprchildsite.py

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
class XPRChildSite:
    """
    Site information.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fConnectionState:str = None
        self._fDateModified:datetime = None
        self._fDescription:str = None
        self._fDisplayName:str = None
        self._fId:str = None
        self._fName:str = None
        self._fServiceAccount:str = None
        self._fSynchronizationStatus:int = -1
        self._fVersion:str = None


    @property
    def ConnectionState(self) -> str:
        """ 
        State of the connection to the parent site.

        Returns:
            The ConnectionState property value.
        """
        return self._fConnectionState

    @ConnectionState.setter
    def ConnectionState(self, value:str) -> None:
        """ 
        Sets the ConnectionState property value.
        """
        self._fConnectionState = value


    @property
    def DateModified(self) -> datetime:
        """ 
        Date and time (in UTC format) that the child site entry was last modified.

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
        A description of the child site.

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
        The globally unique identifier of the child site.

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
        Name of the child site.

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
    def ServiceAccount(self) -> str:
        """ 
        Service account under which the management server is running.

        Returns:
            The ServiceAccount property value.
        """
        return self._fServiceAccount

    @ServiceAccount.setter
    def ServiceAccount(self, value:str) -> None:
        """ 
        Sets the ServiceAccount property value.
        """
        self._fServiceAccount = value


    @property
    def SynchronizationStatus(self) -> int:
        """ 
        Status of the last synchronization of the hierarchy.  

        Returns:
            The SynchronizationStatus property value.
        """
        return self._fSynchronizationStatus

    @SynchronizationStatus.setter
    def SynchronizationStatus(self, value:int) -> None:
        """ 
        Sets the SynchronizationStatus property value.
        """
        self._fSynchronizationStatus = value


    @property
    def Version(self) -> str:
        """ 
        Version number of the child site's management server.

        Returns:
            The Version property value.
        """
        return self._fVersion

    @Version.setter
    def Version(self, value:str) -> None:
        """ 
        Sets the Version property value.
        """
        self._fVersion = value


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
            if (isinstance(self, XPRChildSite)) and (isinstance(other, XPRChildSite)):
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
            if (isinstance(self, XPRChildSite)) and (isinstance(other, XPRChildSite)):
                return self.Name < other.Name
            return False
