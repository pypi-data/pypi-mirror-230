"""
Module: xprsiteowner.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | AdditionalInformation
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
class XPRSiteOwner:
    """
    Owner information.
    
    Threadsafety:
        This class is fully thread-safe.

    More information about site owner configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_ui/mc_siteinformation_basics.htm">vendor documentation page</a>.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fAdditionalInformation:str = None
        self._fAdminEMail:str = None
        self._fAdminName:str = None
        self._fAdminPhone:str = None
        self._fDisplayName:str = None
        self._fLocationCountry:str = None
        self._fLocationEMail:str = None
        self._fLocationPhone:str = None
        self._fLocationStateProvince:str = None
        self._fLocationStreet:str = None
        self._fLocationZipCode:str = None


    @property
    def AdditionalInformation(self) -> str:
        """ 
        Additional Information details of the site.

        Returns:
            The AdditionalInformation property value.
        """
        return self._fAdditionalInformation

    @AdditionalInformation.setter
    def AdditionalInformation(self, value:str) -> None:
        """ 
        Sets the AdditionalInformation property value.
        """
        self._fAdditionalInformation = value


    @property
    def AdminEMail(self) -> str:
        """ 
        EMail address used to contact the site administrator.

        Returns:
            The AdminEMail property value.
        """
        return self._fAdminEMail

    @AdminEMail.setter
    def AdminEMail(self, value:str) -> None:
        """ 
        Sets the AdminEMail property value.
        """
        self._fAdminEMail = value


    @property
    def AdminName(self) -> str:
        """ 
        Name of the site administrator.

        Returns:
            The AdminName property value.
        """
        return self._fAdminName

    @AdminName.setter
    def AdminName(self, value:str) -> None:
        """ 
        Sets the AdminName property value.
        """
        self._fAdminName = value


    @property
    def AdminPhone(self) -> str:
        """ 
        Phone number used to contact the site administrator.

        Returns:
            The AdminPhone property value.
        """
        return self._fAdminPhone

    @AdminPhone.setter
    def AdminPhone(self, value:str) -> None:
        """ 
        Sets the AdminPhone property value.
        """
        self._fAdminPhone = value


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
    def LocationCountry(self) -> str:
        """ 
        Country portion of the address used to contact the site location.

        Returns:
            The LocationCountry property value.
        """
        return self._fLocationCountry

    @LocationCountry.setter
    def LocationCountry(self, value:str) -> None:
        """ 
        Sets the LocationCountry property value.
        """
        self._fLocationCountry = value


    @property
    def LocationEMail(self) -> str:
        """ 
        EMail address used to contact the site location.

        Returns:
            The LocationEMail property value.
        """
        return self._fLocationEMail

    @LocationEMail.setter
    def LocationEMail(self, value:str) -> None:
        """ 
        Sets the LocationEMail property value.
        """
        self._fLocationEMail = value


    @property
    def LocationPhone(self) -> str:
        """ 
        Phone number used to contact the site location.

        Returns:
            The LocationPhone property value.
        """
        return self._fLocationPhone

    @LocationPhone.setter
    def LocationPhone(self, value:str) -> None:
        """ 
        Sets the LocationPhone property value.
        """
        self._fLocationPhone = value


    @property
    def LocationStateProvince(self) -> str:
        """ 
        State or Province portion of the address used to contact the site location.

        Returns:
            The LocationStateProvince property value.
        """
        return self._fLocationStateProvince

    @LocationStateProvince.setter
    def LocationStateProvince(self, value:str) -> None:
        """ 
        Sets the LocationStateProvince property value.
        """
        self._fLocationStateProvince = value


    @property
    def LocationStreet(self) -> str:
        """ 
        Street portion of the address used to contact the site location.

        Returns:
            The LocationStreet property value.
        """
        return self._fLocationStreet

    @LocationStreet.setter
    def LocationStreet(self, value:str) -> None:
        """ 
        Sets the LocationStreet property value.
        """
        self._fLocationStreet = value


    @property
    def LocationZipCode(self) -> str:
        """ 
        ZipCode portion of the address used to contact the site location.

        Returns:
            The LocationZipCode property value.
        """
        return self._fLocationZipCode

    @LocationZipCode.setter
    def LocationZipCode(self, value:str) -> None:
        """ 
        Sets the LocationZipCode property value.
        """
        self._fLocationZipCode = value


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "AdminName - AdminEMail"
        """
        return str.format("{0} - {1}", self.AdminName or "", self.AdminEMail or "")


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.AdminName == other.AdminName
        except Exception as ex:
            if (isinstance(self, XPRSiteOwner)) and (isinstance(other, XPRSiteOwner)):
                return self.AdminName == other.AdminName
            return False

    def __lt__(self, other):
        try:
            # the following comparison will fail if the property value is None!  
            # use the following syntax when calling a sort method that uses lambda searches:
            # epColl.sort(AdminName=lambda x: x.AdminName or "", reverse=False)     <- GOOD syntax
            # epColl.sort(AdminName=lambda x: x.AdminName, reverse=False)           <- BAD syntax, as the "x.AdminName" property may be None, and will cause this to fail!
            return self.AdminName < other.AdminName
        except Exception as ex:
            if (isinstance(self, XPRSiteOwner)) and (isinstance(other, XPRSiteOwner)):
                return self.AdminName < other.AdminName
            return False
