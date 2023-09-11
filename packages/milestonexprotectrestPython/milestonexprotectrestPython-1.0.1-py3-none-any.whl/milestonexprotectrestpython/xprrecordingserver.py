"""
Module: xprrecordingserver.py

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
class XPRRecordingServer:
    """
    Recording Server information.
    
    Threadsafety:
        This class is fully thread-safe.

    More information about recording server configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_ui/mc_recordingservers_servers.htm">vendor documentation page</a>.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fActiveWebServerUri:str = None
        self._fDateModified:datetime = None
        self._fDescription:str = None
        self._fDisplayName:str = None
        self._fEnabled:bool = False
        self._fHostName:str = None
        self._fId:str = None
        self._fMulticastServerAddress:str = None
        self._fName:str = None
        self._fPortNumber:int = 0
        self._fPublicAccessEnabled:bool = False
        self._fPublicWebserverHostName:str = None
        self._fPublicWebserverPort:int = 0
        self._fShutdownOnStorageFailure:bool = None
        self._fSiteId:str = None
        self._fSynchronizationTime:int = -1
        self._fTimeZoneName:str = None
        self._fWebServerUri:str = None


    @property
    def ActiveWebServerUri(self) -> str:
        """ 
        Public address of the recording server's web server over the internet.

        Returns:
            The ActiveWebServerUri property value.
        """
        return self._fActiveWebServerUri

    @ActiveWebServerUri.setter
    def ActiveWebServerUri(self, value:str) -> None:
        """ 
        Sets the ActiveWebServerUri property value.
        """
        self._fActiveWebServerUri = value


    @property
    def DateModified(self) -> datetime:
        """ 
        Date and time (in UTC format) that the recording server entry was last modified.

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
        A description of the recording server.

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
        The Enabled status of the recording server - True if Enabled; otherwise False.

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
    def HostName(self) -> str:
        """ 
        The recording server's host name.

        Returns:
            The HostName property value.
        """
        return self._fHostName

    @HostName.setter
    def HostName(self, value:str) -> None:
        """ 
        Sets the HostName property value.
        """
        self._fHostName = value


    @property
    def Id(self) -> str:
        """ 
        The globally unique identifier of the recording server.

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
    def MulticastServerAddress(self) -> str:
        """ 
        The multicast server address of the recording server.

        Returns:
            The MulticastServerAddress property value.
        """
        return self._fMulticastServerAddress

    @MulticastServerAddress.setter
    def MulticastServerAddress(self, value:str) -> None:
        """ 
        Sets the MulticastServerAddress property value.
        """
        self._fMulticastServerAddress = value


    @property
    def Name(self) -> str:
        """ 
        Name of the recording server.

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
    def PortNumber(self) -> int:
        """ 
        Port number to be used for handling web server requests, for example for handling PTZ 
        camera control commands and for browse and live requests from XProtect Smart Client.  
        Default is port 7563.

        Returns:
            The PortNumber property value.
        """
        return self._fPortNumber

    @PortNumber.setter
    def PortNumber(self, value:int) -> None:
        """ 
        Sets the PortNumber property value.
        """
        self._fPortNumber = value


    @property
    def PublicAccessEnabled(self) -> str:
        """ 
        Indicates if the recording server is publicly accessible (True) or private (False).

        Returns:
            The PublicAccessEnabled property value.
        """
        return self._fPublicAccessEnabled

    @PublicAccessEnabled.setter
    def PublicAccessEnabled(self, value:bool) -> None:
        """ 
        Sets the PublicAccessEnabled property value.
        """
        self._fPublicAccessEnabled = value


    @property
    def PublicWebserverHostName(self) -> bool:
        """ 
        Recording server's public web server address.

        Returns:
            The PublicWebserverHostName property value.
        """
        return self._fPublicWebserverHostName

    @PublicWebserverHostName.setter
    def PublicWebserverHostName(self, value:str) -> None:
        """ 
        Sets the PublicWebserverHostName property value.
        """
        self._fPublicWebserverHostName = value


    @property
    def PublicWebserverPort(self) -> int:
        """ 
        Recording server's public web server port number.

        Returns:
            The PublicWebserverPort property value.
        """
        return self._fPublicWebserverPort

    @PublicWebserverPort.setter
    def PublicWebserverPort(self, value:int) -> None:
        """ 
        Sets the PublicWebserverPort property value.
        """
        self._fPublicWebserverPort = value


    @property
    def ShutdownOnStorageFailure(self) -> bool:
        """ 
        Indicates if the recording server will be shut down automatically if a
        storage failure occurs (True) or not (False).

        Returns:
            The ShutdownOnStorageFailure property value.
        """
        return self._fShutdownOnStorageFailure

    @ShutdownOnStorageFailure.setter
    def ShutdownOnStorageFailure(self, value:bool) -> None:
        """ 
        Sets the ShutdownOnStorageFailure property value.
        """
        self._fShutdownOnStorageFailure = value


    @property
    def SiteId(self) -> str:
        """ 
        Globally unique identifier of the Site that defines this recording server.

        Returns:
            The SiteId property value.
        """
        return self._fSiteId

    @SiteId.setter
    def SiteId(self, value:str) -> None:
        """ 
        Sets the SiteId property value.
        """
        self._fSiteId = value


    @property
    def SynchronizationTime(self) -> int:
        """ 
        The SynchronizationTime property value.

        Returns:
            The SynchronizationTime property value.
        """
        return self._fSynchronizationTime

    @SynchronizationTime.setter
    def SynchronizationTime(self, value:int) -> None:
        """ 
        Sets the SynchronizationTime property value.
        """
        self._fSynchronizationTime = value


    @property
    def TimeZoneName(self) -> str:
        """ 
        Time zone that the recording server is located in.

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
    def WebServerUri(self) -> str:
        """ 
        Local address of the recording server's web server. You use the local address, for example, 
        for handling PTZ camera control commands, and for handling browsing and live requests from 
        XProtect Smart Client.  

        The address includes the port number that is used for web server communication (typically port 7563).

        Returns:
            The WebServerUri property value.
        """
        return self._fWebServerUri

    @WebServerUri.setter
    def WebServerUri(self, value:str) -> None:
        """ 
        Sets the WebServerUri property value.
        """
        self._fWebServerUri = value


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
            if (isinstance(self, XPRRecordingServer)) and (isinstance(other, XPRRecordingServer)):
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
            if (isinstance(self, XPRRecordingServer)) and (isinstance(other, XPRRecordingServer)):
                return self.Name < other.Name
            return False
