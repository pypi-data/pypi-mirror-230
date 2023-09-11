"""
Module: xprsite.py

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
class XPRSite:
    """
    Site information.
    
    Threadsafety:
        This class is fully thread-safe.

    More information about Site configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/feature_flags/ff_federatedsites/mc_federatedsiteproperties.htm">vendor documentation page</a>.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fComputerName:str = None
        self._fDateLastStatusHandshake:datetime = None
        self._fDateModified:datetime = None
        self._fDescription:str = None
        self._fDisplayName:str = None
        self._fDomainName:str = None
        self._fId:str = None
        self._fName:str = None
        self._fMasterSiteAddress:str = None
        self._fPhysicalMemory:int = 0
        self._fPlatform:str = None
        self._fProcessors:int = 0
        self._fServiceAccount:str = None
        self._fSynchronizationStatus:int = -1
        self._fTimeZoneName:str = None
        self._fVersion:str = None


    @property
    def ComputerName(self) -> str:
        """ 
        Computer name that is hosting the site.

        Returns:
            The ComputerName property value.
        """
        return self._fComputerName

    @ComputerName.setter
    def ComputerName(self, value:str) -> None:
        """ 
        Sets the ComputerName property value.
        """
        self._fComputerName = value


    @property
    def DateLastStatusHandshake(self) -> datetime:
        """ 
        Date and time (in UTC format) of the last synchronization of the hierarchy.

        Returns:
            The DateLastStatusHandshake property value.
        """
        return self._fDateLastStatusHandshake

    @DateLastStatusHandshake.setter
    def DateLastStatusHandshake(self, value:datetime) -> None:
        """ 
        Sets the DateLastStatusHandshake property value.
        """
        self._fDateLastStatusHandshake = value


    @property
    def DateModified(self) -> datetime:
        """ 
        Date and time (in UTC format) that the site entry was last modified.

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
        A description of the site.

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
    def DomainName(self) -> str:
        """ 
        Domain name of the computer that is hosting the site.

        Returns:
            The DomainName property value.
        """
        return self._fDomainName

    @DomainName.setter
    def DomainName(self, value:str) -> None:
        """ 
        Sets the DomainName property value.
        """
        self._fDomainName = value


    @property
    def Id(self) -> str:
        """ 
        The globally unique identifier of the site.

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
        Name of the site.

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
    def MasterSiteAddress(self) -> str:
        """ 
        URL of the parent site, if this site is defined as a child site.  
        Value is an empty string if this is the master site.

        Returns:
            The MasterSiteAddress property value.
        """
        return self._fMasterSiteAddress

    @MasterSiteAddress.setter
    def MasterSiteAddress(self, value:str) -> None:
        """ 
        Sets the MasterSiteAddress property value.
        """
        self._fMasterSiteAddress = value


    @property
    def PhysicalMemory(self) -> int:
        """ 
        Host computer physical memory amount that the site is limited to using.  
        A value of zero indicates no limit.

        Returns:
            The PhysicalMemory property value.
        """
        return self._fPhysicalMemory

    @PhysicalMemory.setter
    def PhysicalMemory(self, value:int) -> None:
        """ 
        Sets the PhysicalMemory property value.
        """
        self._fPhysicalMemory = value


    @property
    def Platform(self) -> str:
        """ 
        Host computer platform that the site is running under.  
        A "[Not available]" value is returned if the platform is unavailable.

        Returns:
            The Platform property value.
        """
        return self._fPlatform

    @Platform.setter
    def Platform(self, value:str) -> None:
        """ 
        Sets the Platform property value.
        """
        self._fPlatform = value


    @property
    def Processors(self) -> int:
        """ 
        Host computer number of processors that the site is limited to using.  
        A value of zero indicates no limit.

        Returns:
            The Processors property value.
        """
        return self._fProcessors

    @Processors.setter
    def Processors(self, value:int) -> None:
        """ 
        Sets the Processors property value.
        """
        self._fProcessors = value


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
        It can be either Successful (0) or Failed (1).

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
    def TimeZoneName(self) -> str:
        """ 
        Time zone of the computer that is hosting the site.

        Returns:
            The TimeZoneName property value.
        """
        return self._fTimeZoneName

    @TimeZoneName.setter
    def TimeZoneName(self, value:str) -> None:
        """ 
        Sets the TimeZoneName property value.
        """
        self._fTimeZoneName = value


    @property
    def Version(self) -> str:
        """ 
        Version number of the site's management server.

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
            if (isinstance(self, XPRSite)) and (isinstance(other, XPRSite)):
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
            if (isinstance(self, XPRSite)) and (isinstance(other, XPRSite)):
                return self.Name < other.Name
            return False
