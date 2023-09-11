"""
Module: xprhardware.py

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
from .xprdevice import XPRDevice

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPRHardware:
    """
    Hardware device information.

    More information about Hardware configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_ui/mc_hardwarepropertieswindow.htm">vendor documentation page</a>.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fAddress:str = None
        self._fDateModified:datetime = None
        self._fDescription:str = None
        self._fDisplayName:str = None
        self._fEnabled:bool = False
        self._fHardwareDriverId:str = None
        self._fModel:str = None
        self._fId:str = None
        self._fName:str = None
        self._fPasswordLastModified:datetime = None
        self._fRecordingServerId:str = None
        self._fUserName:str = None


    @property
    def Address(self) -> str:
        """ 
        The host name or IP address of the hardware.

        Returns:
            The Address property value.
        """
        return self._fAddress

    @Address.setter
    def Address(self, value:str) -> None:
        """ 
        Sets the Address property value.
        """
        self._fAddress = value


    @property
    def DateModified(self) -> datetime:
        """ 
        Date and time (in UTC format) that the hardware data was last modified.

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
        A description of the hardware.

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
    def Id(self) -> str:
        """ 
        The globally unique identifier of the hardware.

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
    def Enabled(self) -> str:
        """ 
        The enabled status of the hardware - True if enabled; otherwise False.

        Returns:
            The Enabled property value.
        """
        return self._fEnabled

    @Enabled.setter
    def Enabled(self, value:str) -> None:
        """ 
        Sets the Enabled property value.
        """
        if value != None:
            self._fEnabled = value


    @property
    def HardwareDriverId(self) -> str:
        """ 
        The globally unique identifier of the hardware driver that handles 
        the connection to the hardware.

        Returns:
            The HardwareDriverId property value.
        """
        return self._fHardwareDriverId

    @HardwareDriverId.setter
    def HardwareDriverId(self, value:str) -> None:
        """ 
        Sets the HardwareDriverId property value.
        """
        self._fHardwareDriverId = value


    @property
    def Model(self) -> str:
        """ 
        Identifies the hardware model.

        Returns:
            The Model property value.
        """
        return self._fModel

    @Model.setter
    def Model(self, value:str) -> None:
        """ 
        Sets the Model property value.
        """
        if value != None:
            self._fModel = value


    @property
    def Name(self) -> str:
        """ 
        Name of the hardware device.

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
    def PasswordLastModified(self) -> datetime:
        """ 
        Date and time stamp of the latest password change based on the local time settings 
        of the computer that the password was changed from.

        Returns:
            The PasswordLastModified property value.
        """
        return self._fPasswordLastModified

    @PasswordLastModified.setter
    def PasswordLastModified(self, value:datetime) -> None:
        """ 
        Sets the PasswordLastModified property value.
        """
        self._fPasswordLastModified = value


    @property
    def RecordingServerId(self) -> str:
        """ 
        The globally unique identifier of the parent recording server.

        Returns:
            The RecordingServerId property value.
        """
        return self._fRecordingServerId

    @RecordingServerId.setter
    def RecordingServerId(self, value:str) -> None:
        """ 
        Sets the RecordingServerId property value.
        """
        self._fRecordingServerId = value


    @property
    def UserName(self) -> str:
        """ 
        User name used to authenticate to the hardware, if it is password protected.

        Returns:
            The UserName property value.
        """
        return self._fUserName

    @UserName.setter
    def UserName(self, value:str) -> None:
        """ 
        Sets the UserName property value.
        """
        self._fUserName = value


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
            if (isinstance(self, XPRHardware )) and (isinstance(other, XPRHardware )):
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
            if (isinstance(self, XPRHardware )) and (isinstance(other, XPRHardware )):
                return self.Name < other.Name
            return False
