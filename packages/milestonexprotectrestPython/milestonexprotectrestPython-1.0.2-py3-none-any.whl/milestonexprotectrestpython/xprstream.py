"""
Module: xprstream.py

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
# none

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPRStream:
    """
    Stream information.
    
    Threadsafety:
        This class is fully thread-safe.

    More information about camera stream configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_mcnodes/sf_3devices/mc_addastream_devices.htm">vendor documentation page</a>.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fDefaultPlayback:bool = None
        self._fDisplayName:str = None
        self._fLiveDefault:bool = None
        self._fLiveMode:str = None
        self._fName:str = None
        self._fParentId:str = None
        self._fParentType:str = None
        self._fRecordToId:str = None
        self._fStreamReferenceId:str = None
        self._fUseEdge:bool = None


    @property
    def DefaultPlayback(self) -> bool:
        """ 
        If True, this stream will be delivered to the client if adaptive playback is not configured.  
        otherwise, False.

        Returns:
            The DefaultPlayback property value.
        """
        return self._fDefaultPlayback

    @DefaultPlayback.setter
    def DefaultPlayback(self, value:bool) -> None:
        """ 
        Sets the DefaultPlayback property value.
        """
        self._fDefaultPlayback = value


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
        Globally unique identifier of the stream.  

        Returns:
            The StreamReferenceId property value.

        Note that this is a duplicate property of the StreamReferenceId property.  It was
        added for ease-of-use, as most of the other item classes have an "Id" property.
        """
        return self._fStreamReferenceId

    @Id.setter
    def Id(self, value:str) -> None:
        """ 
        Sets the StreamReferenceId property value.
        """
        self._fStreamReferenceId = value


    @property
    def LiveDefault(self) -> bool:
        """ 
        If True, this stream will be used if the client does not request a specific stream and 
        adaptive streaming is disabled; otherwise, False.

        Returns:
            The LiveDefault property value.
        """
        return self._fLiveDefault

    @LiveDefault.setter
    def LiveDefault(self, value:bool) -> None:
        """ 
        Sets the LiveDefault property value.
        """
        self._fLiveDefault = value


    @property
    def LiveMode(self) -> str:
        """ 
        Specifies when live streaming is needed:  
        - Always: the stream runs even if no XProtect Smart Client users request the stream.  
        - Never: the stream is off. Only use this for recording streams, for example, if you want recordings in high quality and need the bandwidth.  
        - WhenNeeded: the stream starts when requested by any client or if the stream is set to record.  

        Returns:
            The LiveMode property value.
        """
        return self._fLiveMode

    @LiveMode.setter
    def LiveMode(self, value:str) -> None:
        """ 
        Sets the LiveMode property value.
        """
        self._fLiveMode = value


    @property
    def Name(self) -> str:
        """ 
        Name of the stream.

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
    def ParentId(self) -> str:
        """ 
        Globally unique identifier of the parent device.

        Returns:
            The ParentId property value.
        """
        return self._fParentId

    @ParentId.setter
    def ParentId(self, value:str) -> None:
        """ 
        Sets the ParentId property value.
        """
        self._fParentId = value


    @property
    def ParentType(self) -> str:
        """ 
        Parent device type ("cameras", etc).

        Returns:
            The ParentType property value.
        """
        return self._fParentType

    @ParentType.setter
    def ParentType(self, value:str) -> None:
        """ 
        Sets the ParentType property value.
        """
        self._fParentType = value


    @property
    def RecordToId(self) -> str:
        """ 
        Globally unique identifier of the stream.

        Returns:
            The RecordToId property value.
        """
        return self._fRecordToId

    @RecordToId.setter
    def RecordToId(self, value:str) -> None:
        """ 
        Sets the RecordToId property value.
        """
        self._fRecordToId = value


    @property
    def StreamReferenceId(self) -> str:
        """ 
        Globally unique identifier of the stream.

        For adaptive playback, you need to create a stream of each type.  
        The video that is played back is sourced from the primary video stream and secondary streaming is included when required.  
        There must always be a primary recording. Also, the stream that you configure as Primary is used in different contexts 
        such as for motion detection and for export from XProtect Smart Client.

        Returns:
            The StreamReferenceId property value.
        """
        return self._fStreamReferenceId

    @StreamReferenceId.setter
    def StreamReferenceId(self, value:str) -> None:
        """ 
        Sets the StreamReferenceId property value.
        """
        self._fStreamReferenceId = value


    @property
    def UseEdge(self) -> bool:
        """ 
        True if this stream will use edge recordings; otherwise, False.

        Returns:
            The UseEdge property value.
        """
        return self._fUseEdge

    @UseEdge.setter
    def UseEdge(self, value:bool) -> None:
        """ 
        Sets the UseEdge property value.
        """
        self._fUseEdge = value


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
            if (isinstance(self, XPRStream)) and (isinstance(other, XPRStream)):
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
            if (isinstance(self, XPRStream)) and (isinstance(other, XPRStream)):
                return self.Name < other.Name
            return False
