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

# get smartinspect logger reference.
from smartinspectpython.siauto import SISession

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPRRestServiceException(XPRException):
    """
    Raised when the XProtect REST server returns an error response to a REST service call.
    """

    MSG_SERVICE_FAILURE:str = """
XProtect REST Service Failure Details:
Status Code: {0} - {1}
Error Text: {2}
Error ID: {3}
Property Name: {4}
"""
    """
    REST Service failure details message text, in the form of:

    XProtect REST Service Failure Details:
    Status Code: {0} - {1}
    Error Text: {2}
    Error ID: {3}
    Property Name: {4}
    """


    def __init__(self, message:str, errorText:str, errorTextId:str, propertyName:str, httpCode:int, httpReason:str, logsi:SISession=None) -> None:
        """
        Initializes a new instance of the class.

        Args:
            message (str):
                Exception message text.
            errorText (str):
                Error text that describes the error.
            errorTextId (str):
                Error text unique identifier that describes the error.  
            propertyName (str):
                Property name that caused the error.  
            httpCode (str):
                HTTP status code of the error.
            httpReason (str):
                HTTP reason for the error.
            logsi (SISession):
                Trace session object that this exception will be logged to, or null to bypass trace logging.
        """

        # format REST error details.
        restDetails = XPRRestServiceException.FormatRestFailureDetails(errorText, errorTextId, propertyName, httpCode, httpReason)

        # initialize base class, including REST error details as part of the original message text.
        super().__init__(message + restDetails, logsi=logsi)

        # initialize instance.
        self._fErrorText:str = errorText
        self._fErrorTextId:str = errorTextId
        self._fHttpCode:int = httpCode
        self._fHttpReason:str = httpReason
        self._fPropertyName:str = propertyName


    @property
    def ErrorText(self) -> str:
        """ 
        Error text that describes the error.
        This value is parsed from the XProtext REST response "errorText" value.

        Returns:
            The ErrorText property value.
        """
        return self._fErrorText


    @property
    def ErrorTextId(self) -> str:
        """ 
        Error text unique identifier that describes the error.  
        This value is parsed from the XProtext REST response "errorTextId" value.
        This is normally only populated for HTTP status code 400 (Bad Request) errors.

        Returns:
            The ErrorTextId property value.
        """
        return self._fErrorTextId


    @property
    def HttpCode(self) -> int:
        """ 
        HTTP status code of the error.
        This value is copied from the HTTP Response "status_code" value.

        Returns:
            The HttpCode property value.
        """
        return self._fHttpCode


    @property
    def HttpReason(self) -> str:
        """ 
        HTTP reason for the error.
        This value is copied from the HTTP Response "reason" value.

        Returns:
            The HttpReason property value.
        """
        return self._fHttpReason


    @property
    def PropertyName(self) -> str:
        """ 
        Property name that caused the error.  
        This value is parsed from the XProtext REST response "propertyName" value.
        This is normally only populated for HTTP status code 400 (Bad Request) errors.

        Returns:
            The PropertyName property value.
        """
        return self._fPropertyName


    @staticmethod
    def FormatRestFailureDetails(errorText:str, errorTextId:str, propertyName:str, httpCode:int, httpReason:str) -> str:
        """
        Returns a formatted message that describes the REST failure; this
        includes the error text, error text id, http code, http reason, 
        message, and property name.
        

        Args:
            errorText (str):
                Error text that describes the error.
            errorTextId (str):
                Error text unique identifier that describes the error.  
            propertyName (str):
                Property name that caused the error.  
            httpCode (str):
                HTTP status code of the error.
            httpReason (str):
                HTTP reason for the error.

        Returns:
            A formatted string representation of the object.
        """
        # format message to return.
        result:str = XPRRestServiceException.MSG_SERVICE_FAILURE.format(
            str(httpCode),
            httpReason,
            errorText,
            errorTextId,
            propertyName
            )
        return result


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "{Message}"
        """
        return "{0}".format(self.Message)
