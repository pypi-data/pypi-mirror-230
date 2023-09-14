"""
Module: xpreventtype.py

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
class XPREventType:
    """
    Event Type information.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fBuiltIn:bool = None
        self._fCounterEventID:str = None
        self._fDateModified:datetime = None
        self._fDescription:str = None
        self._fDisplayName:str = None
        self._fEventTypeGroupId:str = None
        self._fGeneratorGroupId:str = None
        self._fGeneratorGroupName:str = None
        self._fGeneratorId:str = None
        self._fGeneratorName:str = None
        self._fGeneratorSubType:str = None
        self._fGeneratorType:str = None
        self._fId:str = None
        self._fName:str = None
        self._fOccursGlobally:bool = None
        self._fSourceArray:list = []
        self._fSourceFilterArray:list = []
        self._fState:str = None
        self._fStateGroupId:str = None


    @property
    def BuiltIn(self) -> bool:
        """ 
        The BuiltIn status of the item - True if BuiltIn; otherwise False.

        Returns:
            The BuiltIn property value.
        """
        return self._fBuiltIn

    @BuiltIn.setter
    def BuiltIn(self, value:bool) -> None:
        """ 
        Sets the BuiltIn property value.
        """
        if value != None:
            self._fBuiltIn = value


    @property
    def CounterEventID(self) -> bool:
        """ 
        Globally unique identifier of the Counter event that relates to this event.

        Returns:
            The CounterEventID property value.

        For example ... if this event type were a "Start Recording" event, then it's counter
        event would be the "Stop Recording" event.
        """
        return self._fCounterEventID

    @CounterEventID.setter
    def CounterEventID(self, value:bool) -> None:
        """ 
        Sets the CounterEventID property value.
        """
        if value != None:
            self._fCounterEventID = value


    @property
    def DateModified(self) -> datetime:
        """ 
        Date and time (in UTC format) that the item was last modified.

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
        A description of the event type.

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
    def EventTypeGroupId(self) -> str:
        """ 
        Globally unique identifier of the parent EventTypeGroup.

        Returns:
            The EventTypeGroupId property value.
        """
        return self._fEventTypeGroupId

    @EventTypeGroupId.setter
    def EventTypeGroupId(self, value:str) -> None:
        """ 
        Sets the EventTypeGroupId property value.
        """
        self._fEventTypeGroupId = value


    @property
    def GeneratorGroupId(self) -> str:
        """ 
        Globally unique identifier of the originating group.

        Returns:
            The GeneratorGroupId property value.
        """
        return self._fGeneratorGroupId

    @GeneratorGroupId.setter
    def GeneratorGroupId(self, value:str) -> None:
        """ 
        Sets the GeneratorGroupId property value.
        """
        self._fGeneratorGroupId = value


    @property
    def GeneratorGroupName(self) -> str:
        """ 
        Name of the originating group.

        Returns:
            The GeneratorGroupName property value.
        """
        return self._fGeneratorGroupName

    @GeneratorGroupName.setter
    def GeneratorGroupName(self, value:str) -> None:
        """ 
        Sets the GeneratorGroupName property value.
        """
        self._fGeneratorGroupName = value


    @property
    def GeneratorId(self) -> str:
        """ 
        Globally unique identifier of the originator.

        Returns:
            The GeneratorId property value.
        """
        return self._fGeneratorId

    @GeneratorId.setter
    def GeneratorId(self, value:str) -> None:
        """ 
        Sets the GeneratorId property value.
        """
        self._fGeneratorId = value


    @property
    def GeneratorName(self) -> str:
        """ 
        Name of the originator.

        Returns:
            The GeneratorName property value.
        """
        return self._fGeneratorName

    @GeneratorName.setter
    def GeneratorName(self, value:str) -> None:
        """ 
        Sets the GeneratorName property value.
        """
        self._fGeneratorName = value


    @property
    def GeneratorSubType(self) -> str:
        """ 
        Sub-type of the originator.

        Returns:
            The GeneratorSubType property value.
        """
        return self._fGeneratorSubType

    @GeneratorSubType.setter
    def GeneratorSubType(self, value:str) -> None:
        """ 
        Sets the GeneratorSubType property value.
        """
        self._fGeneratorSubType = value


    @property
    def GeneratorType(self) -> str:
        """ 
        Type of the originator.

        Returns:
            The GeneratorType property value.
        """
        return self._fGeneratorType

    @GeneratorType.setter
    def GeneratorType(self, value:str) -> None:
        """ 
        Sets the GeneratorType property value.
        """
        self._fGeneratorType = value


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
        Name of the entry type.

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
    def OccursGlobally(self) -> bool:
        """ 
        True if the event type occurs globally; otherwise, False.

        Returns:
            The OccursGlobally property value.
        """
        return self._fOccursGlobally

    @OccursGlobally.setter
    def OccursGlobally(self, value:bool) -> None:
        """ 
        Sets the OccursGlobally property value.
        """
        self._fOccursGlobally = value


    @property
    def SourceArray(self) -> list[str]:
        """ 
        Source item types.  
        Contains an array of possible sources of the event.  
        Can contain Camera, Hardware and other itemtype values.  
        For MIP plugin events the source itemtype is MIPItem and the filter contains the MIP Kind of source. 
        The actual source is selected in the rule and alarm definition configuration.

        Returns:
            The SourceArray property value.
        """
        return self._fSourceArray

    @SourceArray.setter
    def SourceArray(self, value:list[str]) -> None:
        """ 
        Sets the SourceArray property value.
        """
        if (value != None):        
            self._fSourceArray = value


    @property
    def SourceFilterArray(self) -> list[str]:
        """ 
        Source filters.   
        Contains an array where the index is matching the sources.  
        Content is formatted as {value} or {type},{value}.  
        If source is "MIPItem" this value is the kind as defined in MIPKind (e.g. "3b559f2e-3693-5463-a6fb-005c1f0259dc").

        Returns:
            The SourceFilterArray property value.
        """
        return self._fSourceFilterArray

    @SourceFilterArray.setter
    def SourceFilterArray(self, value:list[str]) -> None:
        """ 
        Sets the SourceFilterArray property value.
        """
        if (value != None):        
            self._fSourceFilterArray = value


    @property
    def State(self) -> str:
        """ 
        State of the event type (e.g. "Warning", "Error", "Idle", etc).

        Returns:
            The State property value.
        """
        return self._fState

    @State.setter
    def State(self, value:str) -> None:
        """ 
        Sets the State property value.
        """
        self._fState = value


    @property
    def StateGroupId(self) -> str:
        """ 
        State group ID.  
        An event type can belong at most to one state group.  
        All event types with the same state group ID are used to determine the state of a source. 
        A source can be related to more than one state group. For example, a camera source is 
        related to at least two state groups: The motion state group and the recording state group. 

        Event types motion started and stopped in the motion state group determine whether something 
        is moving inside the frame. Together, event types recording started and stopped in the recording 
        state group determine whether the camera stream is being recorded.

        Returns:
            The StateGroupId property value.
        """
        return self._fStateGroupId

    @StateGroupId.setter
    def StateGroupId(self, value:str) -> None:
        """ 
        Sets the StateGroupId property value.
        """
        self._fStateGroupId = value


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
            if (isinstance(self, XPREventType )) and (isinstance(other, XPREventType )):
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
            if (isinstance(self, XPREventType )) and (isinstance(other, XPREventType )):
                return self.DisplayName < other.DisplayName
            return False
