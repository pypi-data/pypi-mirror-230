"""
Module: xprlicenseinformation.py

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
class XPRLicenseInformation:
    """
    License information.
    
    Threadsafety:
        This class is fully thread-safe.

    More information about License configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_licensing/mc_licenseinformationpageui.htm">vendor documentation page</a>.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fActivationAutomatic:bool = None
        self._fCareLevel:str = None
        self._fCareId:str = None
        self._fDisplayName:str = None
        self._fId:str = None
        self._fSoftwareLicenseCode:str = None
        self._fSku:str = None


    @property
    def ActivationAutomatic(self) -> bool:
        """ 
        True if automatic license activation is enabled; otherwise, False.

        Returns:
            The ActivationAutomatic property value.
        """
        return self._fActivationAutomatic

    @ActivationAutomatic.setter
    def ActivationAutomatic(self, value:str) -> None:
        """ 
        Sets the ActivationAutomatic property value.
        """
        self._fActivationAutomatic = value


    @property
    def CareLevel(self) -> str:
        """ 
        Care Level identifier.

        Returns:
            The CareLevel property value.
        """
        return self._fCareLevel

    @CareLevel.setter
    def CareLevel(self, value:str) -> None:
        """ 
        Sets the CareLevel property value.
        """
        self._fCareLevel = value


    @property
    def CareId(self) -> str:
        """ 
        Care ID.

        Returns:
            The CareId property value.
        """
        return self._fCareId

    @CareId.setter
    def CareId(self, value:str) -> None:
        """ 
        Sets the CareId property value.
        """
        self._fCareId = value


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
        The globally unique identifier of the license information.

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


    @property
    def Sku(self) -> str:
        """ 
        Product SKU identifier.

        Returns:
            The Sku property value.
        """
        return self._fSku

    @Sku.setter
    def Sku(self, value:str) -> None:
        """ 
        Sets the Sku property value.
        """
        self._fSku = value


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
            if (isinstance(self, XPRLicenseInformation)) and (isinstance(other, XPRLicenseInformation)):
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
            if (isinstance(self, XPRLicenseInformation)) and (isinstance(other, XPRLicenseInformation)):
                return self.DisplayName < other.DisplayName
            return False
