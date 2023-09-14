"""
Module: xprdevice.py

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
class XPRDevice:
    """
    Device information base class.
    
    More information about Device configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/latest/en-US/standard_features/sf_mc/sf_ui/mc_devicestabs_devices.htm#MC_InfoTabExplained.htm">vendor documentation page</a>.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fChannel:int = 0
        self._fCoverageDirection:float = 0
        self._fCoverageDepth:float = 0
        self._fCoverageFieldOfView:float = 0
        self._fDateCreated:datetime = None
        self._fDateModified:datetime = None
        self._fDescription:str = None
        self._fDisplayName:str = None
        self._fEnabled:bool = False
        self._fGisPoint:str = None
        self._fHardwareId:str = None
        self._fIcon:int = 0
        self._fId:str = None
        self._fName:str = None
        self._fShortName:str = None


    @property
    def Channel(self) -> int:
        """ 
        The channel number of the device.

        Returns:
            The Channel property value.
        """
        return self._fChannel

    @Channel.setter
    def Channel(self, value:int) -> None:
        """ 
        Sets the Channel property value.
        """
        self._fChannel = value


    @property
    def CoverageDirection(self) -> float:
        """ 
        The viewing coverage direction of the device.

        Returns:
            The CoverageDirection property value.
        """
        return self._fCoverageDirection

    @CoverageDirection.setter
    def CoverageDirection(self, value:float) -> None:
        """ 
        Sets the CoverageDirection property value.
        """
        self._fCoverageDirection = value


    @property
    def CoverageDepth(self) -> float:
        """ 
        The viewing coverage depth of the device.

        Returns:
            The CoverageDepth property value.
        """
        return self._fCoverageDepth

    @CoverageDepth.setter
    def CoverageDepth(self, value:float) -> None:
        """ 
        Sets the CoverageDepth property value.
        """
        self._fCoverageDepth = value


    @property
    def CoverageFieldOfView(self) -> float:
        """ 
        The coverage field of view of the device.

        Returns:
            The CoverageFieldOfView property value.
        """
        return self._fCoverageFieldOfView

    @CoverageFieldOfView.setter
    def CoverageFieldOfView(self, value:float) -> None:
        """ 
        Sets the CoverageFieldOfView property value.
        """
        self._fCoverageFieldOfView = value


    @property
    def DateCreated(self) -> datetime:
        """ 
        Date and time (in UTC format) that the item was created.

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
        Date and time (in UTC format) that the item was last modified.

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
        A description of the device.

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
    def Enabled(self) -> str:
        """ 
        The enabled status of the device - True if enabled; otherwise False.

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
    def GisPoint(self) -> str:
        """ 
        Geographic location of the device in the format latitude, longitude, and potentially altitude.  

        Returns:
            The GisPoint property value.

        The format is "POINT (LATITUDE LONGITUDE)" and if you want to clear the 
        coordinates, the value to use is "POINT EMPTY".  
        Examples: "POINT (55.656932878513 12.3763545558449)" "POINT EMPTY".
        Can also include altitude; if so the format is "POINT (LATITUDE LONGITUDE ALTITUDE)".

        The value determines the position of the device icon on the smart map in XProtect Smart Client.
        """
        return self._fGisPoint

    @GisPoint.setter
    def GisPoint(self, value:str) -> None:
        """ 
        Sets the GisPoint property value.
        """
        self._fGisPoint = value


    @property
    def HardwareId(self) -> str:
        """ 
        The globally unique identifier of the hardware, with which the device is connected.

        Returns:
            The HardwareId property value.
        """
        return self._fHardwareId

    @HardwareId.setter
    def HardwareId(self, value:str) -> None:
        """ 
        Sets the HardwareId property value.
        """
        self._fHardwareId = value


    @property
    def Icon(self) -> int:
        """ 
        Icon identifier. The relevant device icon to show.

        Returns:
            The Icon property value.
        """
        return self._fIcon

    @Icon.setter
    def Icon(self, value:int) -> None:
        """ 
        Sets the Icon property value.
        """
        if value != None:
            self._fIcon = value


    @property
    def Id(self) -> str:
        """ 
        The globally unique identifier of the device.

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
        Name of the device.

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
    def ShortName(self) -> str:
        """ 
        Short name. Used as name in the user interface where appropriate.

        Returns:
            The ShortName property value.

        The maximum length of characters is 128.
        """
        return self._fShortName

    @ShortName.setter
    def ShortName(self, value:str) -> None:
        """ 
        Sets the ShortName property value.
        """
        self._fShortName = value


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
            if (isinstance(self, XPRDevice )) and (isinstance(other, XPRDevice )):
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
            if (isinstance(self, XPRDevice )) and (isinstance(other, XPRDevice )):
                return self.Name < other.Name
            return False
