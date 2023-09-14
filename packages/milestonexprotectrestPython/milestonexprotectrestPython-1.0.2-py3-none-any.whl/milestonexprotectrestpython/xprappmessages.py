"""
Module: xprappmessages.py

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
class XPRAppMessages:
    """
    A strongly-typed resource class, for looking up localized strings, etc.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    UNHANDLED_EXCEPTION:str = "XPR0001E - An unhandled exception occured while processing method \"{0}\".\n{1}\n"
    """
    XPR0001E - An unhandled exception occured while processing method \"{0}\".
    {1}
    """

    EXCEPTION_PARSE_REST_RESULTS:str = "XPR0002E - An exception occured while parsing XProtect REST results for \"{0}\" details. \n{1}\n"
    """
    XPR0002E - An exception occured while parsing XProtect REST results for \"{0}\" details.
    {1}
    """

    EXCEPTION_REST_ERROR_BASE:str = "XPR0003E - \"{0}\" method call failed due to a failure response returned by XProtect REST services."
    """
    XPR0003E - \"{0}\" method call failed due to a failure response returned by XProtect REST services.
    """

    EXCEPTION_REST_STATUS_UNKNOWN:str = "XPR0004E - An unknown XProtect REST server response status code was returned:\nStatus Code = {0}\nJSON Response:\n{1}\n\n"
    """
    XPR0004E - An unknown XProtect REST server response code and body was returned:
    Status Code = {0}
    JSON Response:
    {1}
    """

    EXCEPTION_LOGININFO_NOT_SUPPLIED:str = "XPR0005E - LoginInfo object not established.  You must first issue a Login call to establish a LoginInfo object that will be used on subsequent calls to XProtect REST services."
    """
    XPR0005E - LoginInfo object not established.  You must first issue a Login call to 
    establish a LoginInfo object that will be used on subsequent calls to XProtect REST services.
    """

    ARGUMENT_TYPE_ERROR:str = "XPR0006E - {0} argument must be of type \"{1}\"; the \"{2}\" type is not supported for this argument."
    """
    XPR0006E - {0} argument must be of type \"{1}\"; the \"{2}\" type not is supported for this argument.
    """

    ARGUMENT_REQUIRED_ERROR:str = "XPR0007E - The \"{0}\" argument is required, and cannot be null / None."
    """
    XPR0007E - The \"{0}\" argument is required, and cannot be null / None.
    """

    COLLECTION_ARGUMENT_TYPE_ERROR:str = "XPR0008E - Collection \"{0}\" method \"{1}\" argument must be of type \"{2}\"; an object of type \"{3}\" is not supported for this method argument."
    """
    XPR0008E - Collection \"{0}\" method \"{1}\" argument must be of type \"{2}\"; an object of type \"{3}\" is not supported for this method argument.
    """
