"""
Module: xprgenericevent.py

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
class XPRGenericEvent:
    """
    Generic Event information.
    
    More information about Generic Event configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_ui/mc_genericevents_rande.htm">vendor documentation page</a>.

    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fDataSource:str = None
        self._fDateModified:datetime = None
        self._fDisplayName:str = None
        self._fEnabled:bool = None
        self._fExpression:str = None
        self._fExpressionType:str = None
        self._fId:str = None
        self._fName:str = None
        self._fPriority:int = None


    @property
    def DataSource(self) -> str:
        """ 
        Name of the data source.

        Returns:
            The DataSource property value.
        """
        return self._fDataSource

    @DataSource.setter
    def DataSource(self, value:str) -> None:
        """ 
        Sets the DataSource property value.
        """
        self._fDataSource = value


    @property
    def DateModified(self) -> datetime:
        """ 
        Date and time (in UTC format) that the entry was last modified.

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
        True if the event is enabled; otherwise, False.

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
    def Expression(self) -> str:
        """ 
        Expression that the system should look out for when analyzing data packages.

        Returns:
            The Expression property value.
        """
        return self._fExpression

    @Expression.setter
    def Expression(self, value:str) -> None:
        """ 
        Sets the Expression property value.
        """
        self._fExpression = value


    @property
    def ExpressionType(self) -> str:
        """ 
        Indicates how particular the system should be when analyzing received data packages.  
        The options are the following:  
        - Search: In order for the event to occur, the received data package must contain the text specified in the Expression field, but may also have more content.  
        - Match: In order for the event to occur, the received data package must contain exactly the text specified in the Expression field, and nothing else.  
        - Regular expression.  

        Returns:
            The ExpressionType property value.
        """
        return self._fExpressionType

    @ExpressionType.setter
    def ExpressionType(self, value:str) -> None:
        """ 
        Sets the ExpressionType property value.
        """
        self._fExpressionType = value


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
        Name of the event.

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
    def Priority(self) -> int:
        """ 
        Priority of the event.

        The priority must be specified as a number between 0 (highest priority) and 999999 (lowest priority).

        Returns:
            The Priority property value.

        The same data package may be analyzed for different events. The ability to assign a priority to each event 
        lets you manage which event should be triggered if a received package matches the criteria for several events.
        """
        return self._fPriority

    @Priority.setter
    def Priority(self, value:int) -> None:
        """ 
        Sets the Priority property value.
        """
        self._fPriority = value


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
            if (isinstance(self, XPRGenericEvent )) and (isinstance(other, XPRGenericEvent )):
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
            if (isinstance(self, XPRGenericEvent )) and (isinstance(other, XPRGenericEvent )):
                return self.Name < other.Name
            return False
