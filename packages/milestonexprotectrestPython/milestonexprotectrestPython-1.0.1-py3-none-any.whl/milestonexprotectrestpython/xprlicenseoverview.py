"""
Module: xprlicenseoverview.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | CareId
| ---------- | ----------- | ----------------------
| 2023/07/11 | 1.0.0.0     | Initial Version.  

</details>
"""


# external package imports.
# none

# our package imports.
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export

@export
class XPRLicenseOverview:
    """
    License overview information.
    
    Threadsafety:
        This class is fully thread-safe.

    More information about License configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_licensing/mc_LicenseOverviewpageui.htm">vendor documentation page</a>.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fActivatedStatus:str = None
        self._fDisplayName:str = None
        self._fLicenseType:str = None
        self._fPluginId:str = None


    @property
    def ActivatedStatus(self) -> str:
        """ 
        License activation status description.

        Returns:
            The ActivatedStatus property value.
        """
        return self._fActivatedStatus

    @ActivatedStatus.setter
    def ActivatedStatus(self, value:str) -> None:
        """ 
        Sets the ActivatedStatus property value.
        """
        self._fActivatedStatus = value


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
    def LicenseType(self) -> str:
        """ 
        License Type value.

        Returns:
            The LicenseType property value.
        """
        return self._fLicenseType

    @LicenseType.setter
    def LicenseType(self, value:str) -> None:
        """ 
        Sets the LicenseType property value.
        """
        self._fLicenseType = value


    @property
    def PluginId(self) -> str:
        """ 
        The globally unique identifier of the plugin.

        Returns:
            The PluginId property value.
        """
        return self._fPluginId

    @PluginId.setter
    def PluginId(self, value:str) -> None:
        """ 
        Sets the PluginId property value.
        """
        self._fPluginId = value


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "DisplayName - ActivatedStatus"
        """
        return str.format("{0} - {1}", self.DisplayName or "", self.ActivatedStatus or "")


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.DisplayName == other.DisplayName
        except Exception as ex:
            if (isinstance(self, XPRLicenseOverview)) and (isinstance(other, XPRLicenseOverview)):
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
            if (isinstance(self, XPRLicenseOverview)) and (isinstance(other, XPRLicenseOverview)):
                return self.DisplayName < other.DisplayName
            return False
