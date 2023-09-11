"""
Module: xprexception.py

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

# get smartinspect logger reference.
from smartinspectpython.sisession import SISession

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPRException(Exception):
    """
    Exception thrown if a non-fatal application error occurs.
    """
    def __init__(self, message:str, innerException:Exception=None, logsi:SISession=None) -> None:
        """
        Initializes a new class instance using specified message text.

        Args:
            message (str):
                Exception message text.
            innerException (Exception):
                If specified, the exception that caused this exception.  
                Default is None.
            logsi (SISession):
                Trace session object that this exception will be logged to, or null to bypass trace logging.  
                Default is None.
        """

        # initialize base class.
        super().__init__(message)

        # initialize class instance.
        self._fMessage:str = message
        self._fMessageId:str = ""
        self._fInnerException:str = innerException

        # check for message identifier prefix (e.g. "XPR0005E - xxx").
        if (message) and (len(message) > 8):
            if (message.startswith("XPR")):
                if (message[7:8] == "E") or (message[7:8] == "I"):
                    self._fMessageId = message[0:8]  # XPR0005E

        # trace.
        if (logsi):
            if (isinstance(logsi, SISession)):
                if (innerException):
                    logsi.LogException(message, innerException)
                else:
                    logsi.LogError(message)


    @property
    def InnerException(self) -> Exception:
        """ 
        If specified, the exception that caused this exception.  
        Default is None.

        Returns:
            The InnerException property value.
        """
        return self._fInnerException


    @property
    def Message(self) -> str:
        """ 
        Exception message text.

        Returns:
            The Message property value.
        """
        return self._fMessage


    @property
    def MessageId(self) -> str:
        """ 
        Exception message identifier.

        Returns:
            The Message property value.
        """
        return self._fMessage
