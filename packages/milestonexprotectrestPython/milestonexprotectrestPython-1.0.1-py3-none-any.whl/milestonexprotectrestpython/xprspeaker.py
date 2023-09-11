"""
Module: xprspeaker.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/07/11 | 1.0.0.0     | Initial Version.  

</details>
"""


# external package imports.
# none

# our package imports.
from .xprdevice import XPRDevice

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPRSpeaker(XPRDevice):
    """
    Speaker device information.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize base class instance.
        super().__init__()

        # initialize instance.
        self._fEdgeStorageEnabled:bool = False
        self._fEdgeStoragePlaybackEnabled:bool = False
        self._fManualRecordingTimeoutEnabled:bool = False
        self._fManualRecordingTimeoutMinutes:int = 0
        self._fPrebufferEnabled:bool = False
        self._fPrebufferInMemory:bool = False
        self._fPrebufferSeconds:int = 0
        self._fRecordingEnabled:bool = False
        self._fRecordingStorageId:str = None


    @property
    def EdgeStorageEnabled(self) -> bool:
        """ 
        Determines if remote recording is enabled (True) or not (False).

        Returns:
            The EdgeStorageEnabled property value.
        """
        return self._fEdgeStorageEnabled

    @EdgeStorageEnabled.setter
    def EdgeStorageEnabled(self, value:bool) -> None:
        """ 
        Sets the EdgeStorageEnabled property value.
        """
        if value != None:
            self._fEdgeStorageEnabled = value


    @property
    def EdgeStoragePlaybackEnabled(self) -> bool:
        """ 
        Determines if remote recording playback is enabled (True) or not (False).

        Returns:
            The EdgeStoragePlaybackEnabled property value.
        """
        return self._fEdgeStoragePlaybackEnabled

    @EdgeStoragePlaybackEnabled.setter
    def EdgeStoragePlaybackEnabled(self, value:bool) -> None:
        """ 
        Sets the EdgeStoragePlaybackEnabled property value.
        """
        if value != None:
            self._fEdgeStoragePlaybackEnabled = value


    @property
    def ManualRecordingTimeoutEnabled(self) -> bool:
        """ 
        Determines if manual recording timeout is enabled (True) or not (False).

        Returns:
            The ManualRecordingTimeoutEnabled property value.
        """
        return self._fManualRecordingTimeoutEnabled

    @ManualRecordingTimeoutEnabled.setter
    def ManualRecordingTimeoutEnabled(self, value:bool) -> None:
        """ 
        Sets the ManualRecordingTimeoutEnabled property value.
        """
        if value != None:
            self._fManualRecordingTimeoutEnabled = value


    @property
    def ManualRecordingTimeoutMinutes(self) -> int:
        """ 
        Number of minutes to automatically stop all manual recordings started by XProtect Smart 
        Client users if manual recording timeout is enabled.

        Returns:
            The ManualRecordingTimeoutMinutes property value.

        The number of minutes you specify must be sufficiently large enough to accommodate the 
        requirements of the various manual recordings without overloading the system.
        """
        # More information on this property:
        # https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_mcnodes/sf_3devices/mc_managemanualrecording_devices.htm
        return self._fManualRecordingTimeoutMinutes

    @ManualRecordingTimeoutMinutes.setter
    def ManualRecordingTimeoutMinutes(self, value:int) -> None:
        """ 
        Sets the ManualRecordingTimeoutMinutes property value.
        """
        if value != None:
            self._fManualRecordingTimeoutMinutes = value


    @property
    def PrebufferEnabled(self) -> bool:
        """ 
        Determines if pre-buffering is enabled (True) or not (False).

        Returns:
            The PrebufferEnabled property value.

        Pre-buffering is the ability to record audio and video before the actual triggering event occurs.
        """
        # More information on this property:
        # https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_mcnodes/sf_3devices/mc_prebufferingexplained_devices.htm
        return self._fPrebufferEnabled

    @PrebufferEnabled.setter
    def PrebufferEnabled(self, value:bool) -> None:
        """ 
        Sets the PrebufferEnabled property value.
        """
        if value != None:
            self._fPrebufferEnabled = value


    @property
    def PrebufferInMemory(self) -> bool:
        """ 
        Determines if pre-buffering is stored in-memory (True) or onto disk storage (False).

        Returns:
            The PrebufferInMemory property value.

        Storage to memory instead of to disk improves system performance, but is only possible for 
        shorter pre-buffer periods (usually 15 seconds or less).
        """
        # More information on this property:
        # https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_mcnodes/sf_3devices/mc_prebufferingexplained_devices.htm
        return self._fPrebufferInMemory

    @PrebufferInMemory.setter
    def PrebufferInMemory(self, value:bool) -> None:
        """ 
        Sets the PrebufferInMemory property value.
        """
        if value != None:
            self._fPrebufferInMemory = value


    @property
    def PrebufferSeconds(self) -> int:
        """ 
        Number of seconds to automatically stop all manual recordings started by XProtect Smart 
        Client users if manual recording timeout is enabled.

        Returns:
            The PrebufferSeconds property value.

        The number of seconds you specify must be sufficiently large to accommodate your requirements 
        in the various recording rules you define.
        """
        # More information on this property:
        # https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_mcnodes/sf_3devices/mc_prebufferingexplained_devices.htm
        return self._fPrebufferSeconds

    @PrebufferSeconds.setter
    def PrebufferSeconds(self, value:int) -> None:
        """ 
        Sets the PrebufferSeconds property value.
        """
        if value != None:
            self._fPrebufferSeconds = value


    @property
    def RecordingEnabled(self) -> bool:
        """ 
        Determines if recording is enabled (True) or not (False).

        Returns:
            The RecordingEnabled property value.
        """
        return self._fRecordingEnabled

    @RecordingEnabled.setter
    def RecordingEnabled(self, value:bool) -> None:
        """ 
        Sets the RecordingEnabled property value.
        """
        if value != None:
            self._fRecordingEnabled = value


    @property
    def RecordingStorageId(self) -> str:
        """ 
        The Storage identifier of where recordings are stored for this device.  

        Returns:
            The RecordingStorageId property value.
        """
        return self._fRecordingStorageId

    @RecordingStorageId.setter
    def RecordingStorageId(self, value:str) -> None:
        """ 
        Sets the RecordingStorageId property value.
        """
        if value != None:
            self._fRecordingStorageId = value


    # implement sorting support.
    def __eq__(self, other):
        try:
            return self.Name == other.Name
        except Exception as ex:
            if (isinstance(self, XPRSpeaker )) and (isinstance(other, XPRSpeaker )):
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
            if (isinstance(self, XPRSpeaker )) and (isinstance(other, XPRSpeaker )):
                return self.Name < other.Name
            return False
