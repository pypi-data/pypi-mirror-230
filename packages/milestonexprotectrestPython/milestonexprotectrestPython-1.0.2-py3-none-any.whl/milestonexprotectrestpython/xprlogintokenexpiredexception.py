"""
Module: xprrestserviceexception.py

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
from .xprexception import XPRException
from .xprlogininfo import XPRLoginInfo

# get smartinspect logger reference.
from smartinspectpython.siauto import SISession

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPRLoginTokenExpiredException(XPRException):
    """
    Raised when the API service detects that the login token is expired.
    """


    def __init__(self, message:str, logsi:SISession=None) -> None:
        """
        Initializes a new instance of the class.

        Args:
            message (str):
                Exception message text.
            logsi (SISession):
                Trace session object that this exception will be logged to, or null to bypass trace logging.
        """

        # initialize base class, including REST error details as part of the original message text.
        super().__init__(message, logsi=logsi)


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "{Message}"
        """
        return "{0}".format(self.Message)
