"""
Module: xprgenericeventdatasource.py

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
class XPRGenericEventDataSource:
    """
    Generic Event DataSource information.
    
    More information about Generic Event DataSource configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_ui/mc_genericevents_rande.htm?#Genericeventdatasourceproperties">vendor documentation page</a>.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fDataSourceAddressFamily:str = None
        self._fDataSourceAllowedIpv4:str = None
        self._fDataSourceAllowedIpv6:str = None
        self._fDataSourceEcho:str = None
        self._fDataSourceEncoding:int = None
        self._fDataSourceLog:str = None
        self._fDataSourcePort:int = None
        self._fDataSourceProtocol:str = None
        self._fDataSourceSeparator:str = None
        self._fDisplayName:str = None
        self._fEnabled:bool = None
        self._fId:str = None
        self._fName:str = None


    @property
    def DataSourceAddressFamily(self) -> str:
        """ 
        Selectable IP address types: "Internetwork" (IPv4), "InterNetworkV6" (IPv6), or "Both".

        Returns:
            The DataSourceAddressFamily property value.
        """
        return self._fDataSourceAddressFamily

    @DataSourceAddressFamily.setter
    def DataSourceAddressFamily(self, value:str) -> None:
        """ 
        Sets the DataSourceAddressFamily property value.
        """
        self._fDataSourceAddressFamily = value


    @property
    def DataSourceAllowedIpv4(self) -> str:
        """ 
        Allowed external IPv4 addresses.

        Returns:
            The DataSourceAllowedIpv4 property value.

        Specify the IP V4 addresses that the management server must be able to communicate with in order to 
        manage external events. You can also use this to exclude IP addresses that you do not want data from.
        """
        return self._fDataSourceAllowedIpv4

    @DataSourceAllowedIpv4.setter
    def DataSourceAllowedIpv4(self, value:str) -> None:
        """ 
        Sets the DataSourceAllowedIpv4 property value.
        """
        self._fDataSourceAllowedIpv4 = value


    @property
    def DataSourceAllowedIpv6(self) -> str:
        """ 
        Allowed external IPv6 addresses.

        Returns:
            The DataSourceAllowedIpv6 property value.
            
        Specify the IP V6 addresses that the management server must be able to communicate with in order to 
        manage external events. You can also use this to exclude IP addresses that you do not want data from.
        """
        return self._fDataSourceAllowedIpv6

    @DataSourceAllowedIpv6.setter
    def DataSourceAllowedIpv6(self, value:str) -> None:
        """ 
        Sets the DataSourceAllowedIpv6 property value.
        """
        self._fDataSourceAllowedIpv6 = value


    @property
    def DataSourceEcho(self) -> str:
        """ 
        Echo type.

        Returns:
            The DataSourceEcho property value.

        Available echo return formats:  
        - Echo statistics: Echoes the following format: [X],[Y],[Z],[Name of generic event]
          [X] = request number.  
          [Y] = number of characters.  
          [Z] = number of matches with a generic event.  
          [Name of generic event] = name entered in the Name field.  
        - Echo all bytes: Echoes all bytes.  
        - No echo: Suppresses all echoing.  
        """
        return self._fDataSourceEcho

    @DataSourceEcho.setter
    def DataSourceEcho(self, value:str) -> None:
        """ 
        Sets the DataSourceEcho property value.
        """
        self._fDataSourceEcho = value


    @property
    def DataSourceEncoding(self) -> int:
        """ 
        Encoding type code.

        Returns:
            The DataSourceEncoding property value.
        """
        return self._fDataSourceEncoding

    @DataSourceEncoding.setter
    def DataSourceEncoding(self, value:int) -> None:
        """ 
        Sets the DataSourceEncoding property value.
        """
        self._fDataSourceEncoding = value


    @property
    def DataSourceLog(self) -> str:
        """ 
        Log type.

        Returns:
            The DataSourceLog property value.
        """
        return self._fDataSourceLog

    @DataSourceLog.setter
    def DataSourceLog(self, value:str) -> None:
        """ 
        Sets the DataSourceLog property value.
        """
        self._fDataSourceLog = value


    @property
    def DataSourcePort(self) -> int:
        """ 
        Port number of the data source.

        Returns:
            The DataSourcePort property value.
        """
        return self._fDataSourcePort

    @DataSourcePort.setter
    def DataSourcePort(self, value:int) -> None:
        """ 
        Sets the DataSourcePort property value.
        """
        self._fDataSourcePort = value


    @property
    def DataSourceProtocol(self) -> str:
        """ 
        Protocol type.


        Returns:
            The DataSourceProtocol property value.

        Protocols which the system should listen for, and analyze, in order to detect generic events:
        - Any: TCP as well as UDP.  
        - TCP: TCP only.  
        - UDP: UDP only.  

        TCP and UDP packages used for generic events may contain special characters, such as @, #, +, ~, and more.
        """
        return self._fDataSourceProtocol

    @DataSourceProtocol.setter
    def DataSourceProtocol(self, value:str) -> None:
        """ 
        Sets the DataSourceProtocol property value.
        """
        self._fDataSourceProtocol = value


    @property
    def DataSourceSeparator(self) -> str:
        """ 
        Separator bytes used to separate individual generic event records. 
                
        Returns:
            The DataSourceSeparator property value.

        Default for data source type International (see Name property) is 13,10 (e.g. CR,LF).
        """
        return self._fDataSourceSeparator

    @DataSourceSeparator.setter
    def DataSourceSeparator(self, value:str) -> None:
        """ 
        Sets the DataSourceSeparator property value.
        """
        self._fDataSourceSeparator = value


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
    def Enabled(self) -> bool:
        """ 
        True if the data source is enabled; otherwise, False.

        Returns:
            The Enabled property value.
        """
        return self._fEnabled

    @Enabled.setter
    def Enabled(self, value:bool) -> None:
        """ 
        Sets the Enabled property value.
        """
        self._fEnabled = value


    @property
    def Id(self) -> str:
        """ 
        The globally unique identifier of the item.

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
        Name of the item.

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


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "Name - Id"
        """
        return str.format("{0} - {1}", self.Name or "", self.Id or "")


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception as ex:
            if (isinstance(self, XPRGenericEventDataSource )) and (isinstance(other, XPRGenericEventDataSource )):
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
            if (isinstance(self, XPRGenericEventDataSource )) and (isinstance(other, XPRGenericEventDataSource )):
                return self.Name < other.Name
            return False
