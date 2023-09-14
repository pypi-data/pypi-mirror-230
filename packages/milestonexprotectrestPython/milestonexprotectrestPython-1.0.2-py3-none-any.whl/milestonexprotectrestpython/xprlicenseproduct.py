"""
Module: xprlicenseproduct.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | CarePremium
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
class XPRLicenseProduct:
    """
    License product information.
    
    Threadsafety:
        This class is fully thread-safe.

    More information about License configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_licensing/mc_LicenseProductpageui.htm">vendor documentation page</a>.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fCarePlus:str = None
        self._fCarePremium:str = None
        self._fDisplayName:str = None
        self._fExpirationDate:str = None
        self._fProductDisplayName:str = None
        self._fPluginId:str = None
        self._fSoftwareLicenseCode:str = None


    @property
    def CarePlus(self) -> str:
        """ 
        Care Level identifier.

        Returns:
            The CarePlus property value.
        """
        return self._fCarePlus

    @CarePlus.setter
    def CarePlus(self, value:str) -> None:
        """ 
        Sets the CarePlus property value.
        """
        self._fCarePlus = value


    @property
    def CarePremium(self) -> str:
        """ 
        Care ID.

        Returns:
            The CarePremium property value.
        """
        return self._fCarePremium

    @CarePremium.setter
    def CarePremium(self, value:str) -> None:
        """ 
        Sets the CarePremium property value.
        """
        self._fCarePremium = value


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
    def ExpirationDate(self) -> str:
        """ 
        Date and time (in UTC format) of when the license expires.

        Returns:
            The ExpirationDate property value.
        """
        return self._fExpirationDate

    @ExpirationDate.setter
    def ExpirationDate(self, value:str) -> None:
        """ 
        Sets the ExpirationDate property value.
        """
        self._fExpirationDate = value


    @property
    def ProductDisplayName(self) -> str:
        """ 
        Product display name.

        Returns:
            The ProductDisplayName property value.
        """
        return self._fProductDisplayName

    @ProductDisplayName.setter
    def ProductDisplayName(self, value:str) -> None:
        """ 
        Sets the ProductDisplayName property value.
        """
        self._fProductDisplayName = value


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
    def SoftwareLicenseCode(self) -> str:
        """ 
        Product Software License Code value.

        Returns:
            The SoftwareLicenseCode property value.
        """
        return self._fSoftwareLicenseCode

    @SoftwareLicenseCode.setter
    def SoftwareLicenseCode(self, value:str) -> None:
        """ 
        Sets the SoftwareLicenseCode property value.
        """
        self._fSoftwareLicenseCode = value


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "{DisplayName} - {ExpirationDate}"
        """
        return str.format("{0} - {1}", self.DisplayName or "", self.ExpirationDate or "")


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.DisplayName == other.DisplayName
        except Exception as ex:
            if (isinstance(self, XPRLicenseProduct)) and (isinstance(other, XPRLicenseProduct)):
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
            if (isinstance(self, XPRLicenseProduct)) and (isinstance(other, XPRLicenseProduct)):
                return self.DisplayName < other.DisplayName
            return False
