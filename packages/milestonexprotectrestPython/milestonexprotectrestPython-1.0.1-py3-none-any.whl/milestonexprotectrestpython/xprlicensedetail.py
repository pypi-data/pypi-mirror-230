"""
Module: xprlicensedetail.py

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
class XPRLicenseDetail:
    """
    License detail information.
    
    Threadsafety:
        This class is fully thread-safe.

    More information about License configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_licensing/mc_LicenseDetailpageui.htm">vendor documentation page</a>.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fActivated:int = 0
        self._fChangesWithoutActivation:str = None
        self._fDisplayName:str = None
        self._fGracePeriodExpired:int = 0
        self._fGracePeriodIn:int = 0
        self._fLicenseType:str = None
        self._fNotLicensed:int = 0
        self._fNote:str = None
        self._fPluginId:str = None


    @property
    def Activated(self) -> int:
        """ 
        Number of licenses that have been activated.

        Returns:
            The Activated property value.
        """
        return self._fActivated

    @Activated.setter
    def Activated(self, value:int) -> None:
        """ 
        Sets the Activated property value.
        """
        self._fActivated = value


    @property
    def ChangesWithoutActivation(self) -> str:
        """ 
        Number of used device changes without activation licenses.

        Returns:
            The ChangesWithoutActivation property value.
        """
        return self._fChangesWithoutActivation

    @ChangesWithoutActivation.setter
    def ChangesWithoutActivation(self, value:str) -> None:
        """ 
        Sets the ChangesWithoutActivation property value.
        """
        self._fChangesWithoutActivation = value


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
    def GracePeriodIn(self) -> int:
        """ 
        Number of licenses that you have not yet activated and that therefore run in a grace period.

        Returns:
            The GracePeriodIn property value.
        """
        return self._fGracePeriodIn

    @GracePeriodIn.setter
    def GracePeriodIn(self, value:int) -> None:
        """ 
        Sets the GracePeriodIn property value.
        """
        self._fGracePeriodIn = value


    @property
    def GracePeriodExpired(self) -> int:
        """ 
        Number of licenses that you have not yet activated and whose grace period has expired.

        Returns:
            The GracePeriodExpired property value.
        """
        return self._fGracePeriodExpired

    @GracePeriodExpired.setter
    def GracePeriodExpired(self, value:int) -> None:
        """ 
        Sets the GracePeriodExpired property value.
        """
        self._fGracePeriodExpired = value


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
    def NotLicensed(self) -> int:
        """ 
        Number of licenses that you have in-use that exceed the number of available licenses.

        Returns:
            The NotLicensed property value.
        """
        return self._fNotLicensed

    @NotLicensed.setter
    def NotLicensed(self, value:int) -> None:
        """ 
        Sets the NotLicensed property value.
        """
        self._fNotLicensed = value


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


    @property
    def Note(self) -> str:
        """ 
        Notes pertaining to the license.

        Returns:
            The Note property value.
        """
        return self._fNote

    @Note.setter
    def Note(self, value:str) -> None:
        """ 
        Sets the Note property value.
        """
        self._fNote = value


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "DisplayName - Activated"
        """
        return str.format("{0} - {1}", self.DisplayName or "", str(self.Activated))


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.DisplayName == other.DisplayName
        except Exception as ex:
            if (isinstance(self, XPRLicenseDetail)) and (isinstance(other, XPRLicenseDetail)):
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
            if (isinstance(self, XPRLicenseDetail)) and (isinstance(other, XPRLicenseDetail)):
                return self.DisplayName < other.DisplayName
            return False
