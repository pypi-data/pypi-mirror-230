"""
Module: xprrestservicebase.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/07/11 | 1.0.0.0     | Initial Version.  

</details>
"""

# external package imports.
import _threading_local
from datetime import datetime, timedelta
import inspect
from requests import Response, Request, Session
from requests_ntlm import HttpNtlmAuth 
from smartinspectpython.sisourceid import SISourceId 
from urllib import parse
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

# our package imports.
from .xprappmessages import XPRAppMessages
from .xprauthenticationtype import XPRAuthenticationType
from .xprexception import XPRException
from .xprlogininfo import XPRLoginInfo
from .xprlogintokenexpiredexception import XPRLoginTokenExpiredException
from .xprrestserviceexception import XPRRestServiceException 
# none

# our package constants.
from .xprconst import (
    MSG_TRACE_PROCESSING_DICTIONARY,
    MSG_TRACE_PROCESSING_DICTIONARY_COLLECTION,
    MSG_TRACE_METHOD_RESTREQUEST,
    MSG_TRACE_METHOD_RESTREQUEST_HEADERS,
    MSG_TRACE_METHOD_RESTREQUEST_BODY,
    MSG_TRACE_METHOD_RESTRESPONSE,
    MSG_TRACE_METHOD_RESTRESPONSE_BODY,
    MSG_TRACE_RESULT_COLLECTION,
    MSG_TRACE_RESULT_OBJECT
)

# get smartinspect logger reference.
from smartinspectpython.siauto import SIAuto, SISession, SILevel
_logsi:SISession = SIAuto.Main

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export, DataTypeHelper


@export
class XPRRestServiceBase:
    """
    The XPRRestServiceBase class provides properties common to all XProtect REST services.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.

        Raises:
            TypeError:
                The loginInfo argument is not of type XPRLoginInfo.
            Exception:
                The method fails for any other reason.
        """
        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            # initialize instance.
            self._fApiGatewayUrlPrefix:str = "http://localhost"
            self._fIsAutoTokenRenewalEnabled = True
            self._fIsSslVerifyEnabled:bool = True
            self._fLoginInfo = None
            self._fLock = _threading_local.RLock()

        except Exception as ex:

            # trace.
            _logsi.LogException(None, ex)
            raise

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    @property
    def ApiGatewayUrlPrefix(self) -> str:
        """ 
        URL prefix of the XProtect REST API Gateway server.

        Returns:
            The ApiGatewayUrlPrefix property value.

        This url prefix is used to call various REST API services that are hosted by the 
        XProtect API Gateway.  

        It should only contain the server name (and port number if required) portion of
        the API Gateway server (e.g. "https://xprotectapigateway.example.com", or
        "https://xprotectapigateway.netlucas.com:443") url prefix.  

        It should NOT contain any of the APi Gateway REST version information (e.g. 
        "/api/rest/v1/") details.
        """
        return self._fApiGatewayUrlPrefix

    @ApiGatewayUrlPrefix.setter
    def ApiGatewayUrlPrefix(self, value:str) -> None:
        """ 
        Sets the ApiGatewayUrlPrefix property value.
        """
        if value != None:
            if (value.endswith("/")):
                value = value[0:len(value)-1]
            self._fApiGatewayUrlPrefix = value


    @property
    def IsAutoTokenRenewalEnabled(self) -> bool:
        """ 
        Enables / disables the automatic token renewal check logic check that is
        made prior to making a call to the XProtect REST service.  

        Returns:
            The IsAutoTokenRenewalEnabled property value.        

        If True, the LoginInfo.ExpireTime value is checked to see if the XProtect token is
        within 1 minute of expiring PRIOR to processing the desired API method (e.g. GetCameras, etc).
        If the token is about to expire, then it will be automatically renewed via a call to the XProtect
        REST Login method (e.g. LoginBasicUser, LoginBasicWindows) that was previously used to login and
        establish the authentication token.  The desired API method (e.g. GetCameras, etc) is then
        processed as requested.
        
        If False, the desired API method (e.g. GetCameras, etc) is processed normally, though it will
        probably fail with a XPRLoginTokenExpiredException due to an expired token!
        """
        return self._fIsAutoTokenRenewalEnabled

    @IsAutoTokenRenewalEnabled.setter
    def IsAutoTokenRenewalEnabled(self, value:bool) -> None:
        """ 
        Sets the IsAutoTokenRenewalEnabled property value.
        """
        if value != None:
            self._fIsAutoTokenRenewalEnabled = value


    @property
    def IsSslVerifyEnabled(self) -> bool:
        """ 
        SSL Verify flag used on all request GET / POST method calls.
        Default Value is True.        

        Returns:
            The IsSslVerifyEnabled property value.        

        This setting will be added to all request GET / POST calls made to the XProtect REST services.

        If False, it will ignore SSL Certificate warnings (e.g. certificate expired, self-signed certificate, etc).
        It also makes a call to "urllib3.disable_warnings(category=InsecureRequestWarning)" to suppress
        terminal messages.
        """
        return self._fIsSslVerifyEnabled

    @IsSslVerifyEnabled.setter
    def IsSslVerifyEnabled(self, value:bool) -> None:
        """ 
        Sets the IsSslVerifyEnabled property value.
        """
        if value != None:
            self._fIsSslVerifyEnabled = value
            if (value == False):
                # suppress only the single warning from urllib3 needed.
                disable_warnings(category=InsecureRequestWarning)


    @property
    def LoginInfo(self) -> XPRLoginInfo:
        """ 
        LoginInfo object that was specified when the class was initialized, or when
        a Login method (e.g. LoginBasicUser, LoginWindowsUser) was called successfully.

        Returns:
            The LoginInfo property value.

        This property is read-only.
        """
        return self._fLoginInfo


    def _AutoTokenRenewalCheck(self, serviceMethodName:str) -> None:
        """
        Checks the LoginInfo.ExpireTime value to see if the XProtect token needs to be renewed.
        Also checks to ensure the LoginInfo property value is set (e.g. a LoginX method has been
        performed).        

        Args:
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Raises:
            XPRException:
                The method fails for any reason.  
        
        The IsAutoTokenRenewalEnabled property controls if the token is checked or not.
        If True, the LoginInfo.ExpireTime value is checked to see if the XProtect token is
        within 1 minute of expiring PRIOR to processing the desired API method (e.g. GetCameras, etc).
        If the token is about to expire, then it will be automatically renewed via a call to the XProtect
        REST Login method (e.g. LoginBasicUser, LoginBasicWindows) that was previously used to login and
        establish the authentication token.  The desired API method (e.g. GetCameras, etc) is then
        processed as requested.
        """
        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 
   
            # validations.
            if (self._fLoginInfo == None):
                raise XPRException(XPRAppMessages.EXCEPTION_LOGININFO_NOT_SUPPLIED, None, _logsi)

            # are we auto-renewing the token?  if not, then we are done.
            if (self.IsAutoTokenRenewalEnabled == False):
                return
            
            # is token within 60 seconds of expiring?
            diffInSeconds:int = (self._fLoginInfo.ExpireTime - datetime.utcnow()).total_seconds() 
            if (diffInSeconds < 60):

                _logsi.LogVerbose("Login token is about to expire; the token will be auto renewed.")

                # yes - renew the token using the appropriate login method.
                if (self._fLoginInfo.AuthenticationType == XPRAuthenticationType.Basic):    
                    self.LoginBasicUser(self._fLoginInfo.UserName, self._fLoginInfo.Password)

                elif (self._fLoginInfo.AuthenticationType == XPRAuthenticationType.Windows):
                    self.LoginWindowsUser(self._fLoginInfo.UserName, self._fLoginInfo.Password)

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)
                    

    def _Parse_Login(self, oDict:dict) -> XPRLoginInfo:
        """
        Converts a Login JSON response to a class.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.

        Returns:
            An XPRLoginInfo class that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "Login"
        loginInfo:XPRLoginInfo = XPRLoginInfo()

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)
            _logsi.LogVerbose("Parsing XProtect REST service response")

            # JSON response example:
            #{
            #  "access_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI1N0ExNjRDQTVCQzA4MjU2RjQ4OTBBRDZEMDJGMDNFIiwidHlwIjoiSldUIn0.eyJpc3MiOiJodHRwOi8vd2luMTB2bS9JRFAiLCJuYmYiOjE2OTE1MjkxNTEsImlhdCI6MTY5MTUyOTE1MSwiZXhwIjoxNjkxNTMyNzUxLCJhdWQiOlsibWFuYWdlbWVudHNlcnZlciIsImh0dHA6Ly93aW4xMHZtL0lEUC9yZXNvdXJjZXMiXSwic2NvcGUiOlsibWFuYWdlbWVudHNlcnZlciJdLCJhbXIiOlsicHdkIl0sImNsaWVudF9pZCI6IkdyYW50VmFsaWRhdG9yQ2xpZW50Iiwic3ViIjoiOTlFNTE1NUItNUZCNi00QzdCLTkxQTgtNzA1OTlGMTEyNDA2IiwiYXV0aF90aW1lIjoxNjkxNTI5MTUxLCJpZHAiOiJsb2NhbCIsIm5hbWUiOiJ4cGFkbWluIiwidXBkYXRlZF9hdCI6IjE2ODg4NDkxMDMiLCJqdGkiOiI4OTZDRTUyMzNBN0Y4N0M0Qzc3RDlBQjZBQjUyQ0M5RSJ9.fIBr1t-TOXoOKU1wJWKdRweQHst48MqrvC9Zg4-ls_i-jNJ1vh-Lcr9aBWleJqZup5EIEVBk9Zt6xskHx4Vxkbpy1vtdN1zuwW38v7KMa2GXNsJHZ8Jc3giIUzoTM1rgSmxx3vTvWaTwew-IKB5eqdeSrQXbJiiEjiUS2lC7aJAcBWr4jhg-za55HDhlOeNnV1bwSIBfot-z0CoVUcISpuYBicx1VYFSKibTBUmovT5Ie3xXYMzNArbBWgQC5XAI1Y3DAumbnypS3zMmAr4ifWCYc9ACETvCA5FN8Hpeij_5o9PCP0VJrcbyLUKgzCVfc3uMNqlBRqBrvtAANuTs-g",
            #  "expires_in": 3600,
            #  "token_type": "Bearer",
            #  "scope": "managementserver"
            #}

            # note - "expires_in" is expressed in seconds (e.g. 3600 seconds / 60 = 60 minutes = 1 hour).

            # parse response result.
            loginInfo.RegistrationTime = datetime.utcnow()
            loginInfo.Scope = self.GetDictKeyValueString(oDict, "scope", True)
            loginInfo.TimeToLiveLimited = True
            loginInfo.TimeToLiveSeconds = self.GetDictKeyValueInt(oDict, "expires_in", True)
            loginInfo.Token = self.GetDictKeyValueString(oDict, "access_token", True)
            loginInfo.TokenType = self.GetDictKeyValueString(oDict, "token_type", True)

            # calculate expire time from registration time and time to live properties.
            loginInfo.ExpireTime = loginInfo.RegistrationTime + timedelta(seconds=loginInfo.TimeToLiveSeconds)
  
            # return login info object.
            return loginInfo

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    @staticmethod
    def AddDictKeyValueArrayStrings(oDict:dict, keyName:str, arrayListStrings:list[str], raiseExceptionIfNotFound:bool=False) -> None:
        """
        Checks a dictionary for the specified key name, ensures that it defines a list of strings, 
        and then appends them to the arrayListStrings argument list; otherwise, no values are appended
        to the arrayListStrings argument.        

        Args:
            oDict (dict):
                Dictionary to check for the specified key name.
            keyName (str):
                Key name to check for.
            arrayListStrings (str):
                An array list of strings to append found values to.
            raiseExceptionIfNotFound (bool):
                True to raise an Exception if the specified keyName is not found in the dictionary;  
                otherwise, False.  
                Default value: False  
        """
        # does dictionary contain the key?
        if (XPRRestServiceBase.DictHasKey(oDict, keyName)):

            valueArray = oDict[keyName]
            
            # is it a list of strings? if so, then append all values to the arrayListStrings argument.
            if (isinstance(valueArray, list)):
                for value in valueArray:
                    if (isinstance(value, str)):
                        arrayListStrings.append(value)
                return      

        else:

            # key was not found - are we raising an exception?  if so, then do it!
            if (raiseExceptionIfNotFound):
                raise Exception("Could not locate key \"{0}\" in response dictionary.".format(keyName))


    def CheckRestResponseCode(self, serviceMethodName:str, req:Request, resp:Response) -> dict:
        """
        Check the REST service HTTP response code for error values (4xx, 5xx, etc).
        An XPRRestServiceException will be thrown if the HTTP status code does not
        equal 200 or 201.

        Args:
            serviceMethodName (str):
                Name of the XProtect REST service method that was called.
                Example: "GetCameras"
            req (Request):
                HTTP request object that contains the REST server request.
            resp (Response):
                HTTP response object that contains the REST server response.

        Returns:
            If HTTP status is successful (e.g. 200, 201) then the JSON response is
            returned as a dictionary; otherwise, an XPRRestServiceException is raised.

        Raises:
            XPRRestServiceException:
                Raised if the HTTP status returned indicated failue (e.g. 4xx, 5xx, etc).
        """
        oDict:dict = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)
            if (_logsi.IsOn(SILevel.Verbose)):
                _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTRESPONSE.format(serviceMethodName), resp)
                _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTRESPONSE_BODY.format(serviceMethodName), resp.text, SISourceId.Xml)

            # if OK response, then convert the JSON response body to dictionary and return it.
            if (resp.status_code == 200) or (resp.status_code == 201):
                oDict = resp.json()
                return oDict

            # check for REST errors that are caused by our client request.
            # for 4xx errors, the response body will contain a JSON object that describes one or more errors.

            # HTTP status code 400 - Client Error, Bad Request.
            if (resp.status_code == 400):
                oDict = resp.json()
                self.RaiseRestServiceException(serviceMethodName, req, resp, oDict)

            # HTTP status code 401 - Client Error, Unauthorized.
            elif (resp.status_code == 401):
                oDict = resp.json()
                self.RaiseRestServiceException(serviceMethodName, req, resp, oDict)

            # HTTP status code 403 - Client Error, Forbidden.
            elif (resp.status_code == 403):
                oDict = resp.json()
                self.RaiseRestServiceException(serviceMethodName, req, resp, oDict)

            # HTTP status code 404 - Client Error, Not Found.
            elif (resp.status_code == 404):
                oDict = resp.json()
                self.RaiseRestServiceException(serviceMethodName, req, resp, oDict)

            # HTTP status code 4xx - Client Error.
            elif (resp.status_code >= 400) and (resp.status_code <= 499):
                oDict = resp.json()
                self.RaiseRestServiceException(serviceMethodName, req, resp, oDict)

            # check for REST errors that are caused by the XProtect REST server.
            # for 5xx errors, the response body MAY contain (not guaranteed) one or more error descriptions
            # in plain text (not JSON data) format.

            # HTTP status code 503 - "The service is unavailable."

            # check for HTTP status code 500 - Server Error, Internal Server Error.
            elif (resp.status_code >= 500) and (resp.status_code <= 599):
                # raise exception.
                message:str = XPRAppMessages.EXCEPTION_REST_ERROR_BASE.format(serviceMethodName)
                raise XPRRestServiceException(message, resp.text, None, None, resp.status_code, resp.reason, _logsi)

            # if we did not process any of the above status codes, then it's an unknown.
            # in this case, we will simply populate the exception details with the HTTP status
            # code and the body of the response object unparsed.
            else:
                raise Exception(XPRAppMessages.EXCEPTION_REST_STATUS_UNKNOWN.format(str(resp.status_code), resp.text))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def RaiseRestServiceException(self, serviceMethodName:str, req:Request, resp:Response, oDict:dict) -> None:
        """
        Parses XProtect REST services failed HTTP response and raises the XPRRestServiceException
        to indicate the requested call failed.

        Args:
            serviceMethodName (str):
                Name of the XProtect REST service method that was called.
                Example: "GetCameras"
            req (Request):
                HTTP request object that contains the REST server request.
            resp (Response):
                HTTP response object that contains the REST server response.
            oDict (dict):
                JSON response dictionary of the called REST service method.

        Raises:
            XPRRestServiceException:
                Thrown if XProtext REST service error response details were parsed successfully.
            XPRException:
                Thrown if XProtext REST service error response details could not be parsed successfully.
        """
        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # initialize exception parameters.
            message:str = XPRAppMessages.EXCEPTION_REST_ERROR_BASE.format(serviceMethodName)
            errorText:str = None
            errorTextId:str = None
            httpCode:int = resp.status_code
            httpReason:str = resp.reason
            propertyName:str = None

            #{
            #  "error": "invalid_grant",
            #  "error_description": "invalid_username_or_password",
            #  "error_code": "LockedOut"
            #}

            #{
            #  "error": {
            #    "httpCode": 400,
            #    "details": [
            #      {
            #        "errorText": "Invalid parent. /CameraFolder"
            #        "errorText": "Device not found. cameras/f0f31f69-36a2-46a3-80b6-48e4bf617db9"
            #      }
            #    ]
            #  }
            #}

            #{
            #  "error": {
            #    "httpCode": 401,
            #    "details": [
            #      {
            #        "errorText": "Token validation failed: the token is expired."
            #      }
            #    ]
            #  }
            #}

            #{
            #  "error": {
            #    "httpCode": 403,
            #    "details": [
            #      {
            #        "errorText": "You do not have sufficient permissions to complete the operation."
            #        "errorTextId": "VMO61008"
            #      }
            #    ]
            #  }
            #}

            #{
            #  "error": {
            #    "httpCode": 404,
            #    "details": [
            #      {
            #        "errorText": "Device not found. cameras/f0f31f69-36a2-46a3-80b6-48e4bf617db9"
            #      }
            #    ]
            #  }
            #}

            # does the dictionary contain the "error" key?
            if (XPRRestServiceBase.DictHasKey(oDict, "error")):

                # is the "error" value a string?
                # this can happen for "invalid_username_or_password" errors.
                if (isinstance(oDict["error"], str)):

                    # get error details.
                    # note - normally issued from a HTTP status = 400 response.
                    errorText = XPRRestServiceBase.GetDictKeyValueString(oDict, "error_description")
                    errorTextId = XPRRestServiceBase.GetDictKeyValueString(oDict, "error")
                    propertyName = XPRRestServiceBase.GetDictKeyValueString(oDict, "error_code")

                # is the "error" value a dictionary?
                elif (isinstance(oDict["error"], dict)):

                    oDictChild = oDict["error"]
                    httpCode = self.GetDictKeyValueInt(oDictChild, "httpCode")

                    # does the dictionary contain the "details" subkey?
                    if (XPRRestServiceBase.DictHasKey(oDictChild, "details")):
                        oDictChild = XPRRestServiceBase.GetDictItems(oDictChild, "details")

                        # get error details.
                        errorText = XPRRestServiceBase.GetDictKeyValueString(oDictChild[0], "errorText")
                        errorTextId = XPRRestServiceBase.GetDictKeyValueString(oDictChild[0], "errorTextId")

                else:
                    pass

            # is this a login token expired event?  if so, then raise a special exception for it.
            if (httpCode == 401) and (errorText.find("token is expired") > -1):
                raise XPRLoginTokenExpiredException(errorText, _logsi)

            # is this a 404 resource not found event?  if so, then add the request URL to the PropertyName field if it's not set.
            if (httpCode == 404) and (propertyName == None):
                propertyName = req.url

            # raise exception.
            raise XPRRestServiceException(message, errorText, errorTextId, propertyName, httpCode, httpReason, _logsi)

        except XPRException: raise  # pass formatted exception on thru
        except Exception as ex:

            # trace and ignore exceptions.
            _logsi.LogObject(SILevel.Error, MSG_TRACE_METHOD_RESTRESPONSE.format(serviceMethodName), resp)
            _logsi.LogSource(SILevel.Error, MSG_TRACE_METHOD_RESTRESPONSE_BODY, resp.text, SISourceId.Xml)
            raise XPRException("An exception occured while processing REST response \"errorText\" details for method \"{0}\"!".format(serviceMethodName), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    @staticmethod
    def DictHasKey(oDict:dict, keyName:str) -> bool:
        """
        Checks a dictionary for the specified key name.

        Args:
            oDict (dict):
                Dictionary to check for the specified key name.
            keyName (str):
                Key name to check for.

        Returns:
            True if the specified key name exists in the dictionary; otherwise, False.
        """
        # validations.
        if (oDict == None):
            return False
        if (keyName == None) or (len(keyName) ==0):
            return False

        # prepare for comparison.
        keyName = keyName.lower()

        # check dictionary for the key name.
        for key in oDict.keys():
            if (key.lower() == keyName):
                return True

        # key name not found - return False.
        return False


    @staticmethod
    def GetDictItems(oDict:dict, keyNameItem:str) -> dict:
        """
        Checks a dictionary for the specified item key name, and verifies it contains at 
        least one occurance.

        Args:
            oDict (dict):
                Dictionary to check for the specified collection key and child item key.
            keyNameItem (str):
                Item Key name to check for that contains a child item.

        Returns:
            A dictionary of item key names, or an empty dictionary if none were found.

        This method is useful for parsing collection responses and their underlying item nodes.  
        For example:  

        <ServiceInfo>  
          <Name />  
        </ServiceInfo>  
        <ServiceInfo>  
          <Name />  
        </ServiceInfo>  
        """
        # by default, return an empty dictionary.
        oResult = {}

        # validations.
        if (oDict == None):
            return oResult
        if (keyNameItem == None) or (len(keyNameItem) == 0):
            return oResult

        # does results dictionary contain the specified collection key?
        if (not XPRRestServiceBase.DictHasKey(oDict, keyNameItem)):
            return oResult

        # trace.
        _logsi.LogVerbose(MSG_TRACE_PROCESSING_DICTIONARY.format(keyNameItem))

        # if only one item in the collection, then it's a single string.
        # in this case, make it an array so it can be processed the same as an array.
        if (not isinstance(oDict[keyNameItem],list)):
            oResult = [oDict[keyNameItem]]
            return oResult

        # return a reference to the collection items.
        return oDict[keyNameItem]


    @staticmethod
    def GetDictKeyValueString(oDict:dict, keyName:str, raiseExceptionIfNotFound:bool=False) -> str:
        """
        Checks a dictionary for the specified key name and returns the value if the
        key exists; otherwise, null is returned.

        Args:
            oDict (dict):
                Dictionary to check for the specified key name.
            keyName (str):
                Key name to check for.
            raiseExceptionIfNotFound (bool):
                True to raise an Exception if the specified keyName is not found in the dictionary;  
                otherwise, False.  
                Default value: False  

        Returns:
            The value of the specified key name if the key exists; otherwise, null.
        """
        # does dictionary contain the key?
        if (XPRRestServiceBase.DictHasKey(oDict, keyName)):

            value = oDict[keyName]

            # is it a string value? if so, then return the value.
            if (isinstance(value, str)):
                return value

        else:

            # key was not found - are we raising an exception?  if so, then do it!
            if (raiseExceptionIfNotFound):
                raise Exception("Could not locate key \"{0}\" in response dictionary.".format(keyName))

        # otherwise, return null.
        return None


    @staticmethod
    def GetDictKeyValueInt(oDict:dict, keyName:str, raiseExceptionIfNotFound:bool=False) -> int:
        """
        Checks a dictionary for the specified key name and returns the value if the
        key exists; otherwise, null is returned.

        Args:
            oDict (dict):
                Dictionary to check for the specified key name.
            keyName (str):
                Key name to check for.
            raiseExceptionIfNotFound (bool):
                True to raise an Exception if the specified keyName is not found in the dictionary;  
                otherwise, False.  
                Default value: False  

        Returns:
            The value of the specified key name if the key exists; otherwise, null.
        """
        # does dictionary contain the key?
        if (XPRRestServiceBase.DictHasKey(oDict, keyName)):

            value = oDict[keyName]

            # is it an integer value? if so, then return the value.
            if (isinstance(value, int)):
                return value

            # is it an string value? if so, then convert it to an integer.
            if (isinstance(value, str)):

                try:
                    return int(value)
                except Exception as ex:
                    return None

        else:

            # key was not found - are we raising an exception?  if so, then do it!
            if (raiseExceptionIfNotFound):
                raise Exception("Could not locate key \"{0}\" in response dictionary.".format(keyName))

        # otherwise, return null.
        return None


    @staticmethod
    def GetDictKeyValueFloat(oDict:dict, keyName:str, raiseExceptionIfNotFound:bool=False) -> float:
        """
        Checks a dictionary for the specified key name and returns the value if the
        key exists; otherwise, null is returned.

        Args:
            oDict (dict):
                Dictionary to check for the specified key name.
            keyName (str):
                Key name to check for.
            raiseExceptionIfNotFound (bool):
                True to raise an Exception if the specified keyName is not found in the dictionary;  
                otherwise, False.  
                Default value: False  

        Returns:
            The value of the specified key name if the key exists; otherwise, null.
        """
        # does dictionary contain the key?
        if (XPRRestServiceBase.DictHasKey(oDict, keyName)):

            value = oDict[keyName]

            # is it a float value? if so, then return the value.
            if (isinstance(value, float)):
                return value

            # is it an integer value? if so, then convert it to float and return the value.
            if (isinstance(value, int)):
                return float(value)

            # is it an string value? if so, then convert it to a float.
            if (isinstance(value, str)):

                try:
                    return float(value)
                except Exception as ex:
                    return None

        else:

            # key was not found - are we raising an exception?  if so, then do it!
            if (raiseExceptionIfNotFound):
                raise Exception("Could not locate key \"{0}\" in response dictionary.".format(keyName))

        # otherwise, return null.
        return None


    @staticmethod
    def GetDictKeyValueBool(oDict:dict, keyName:str, raiseExceptionIfNotFound:bool=False) -> bool:
        """
        Checks a dictionary for the specified key name and returns the value if the
        key exists; otherwise, null is returned.

        Args:
            oDict (dict):
                Dictionary to check for the specified key name.
            keyName (str):
                Key name to check for.
            raiseExceptionIfNotFound (bool):
                True to raise an Exception if the specified keyName is not found in the dictionary;  
                otherwise, False.  
                Default value: False  

        Returns:
            The value of the specified key name if the key exists; otherwise, null.
        """
        # does dictionary contain the key?
        if (XPRRestServiceBase.DictHasKey(oDict, keyName)):

            return DataTypeHelper.BoolFromString(str(oDict[keyName]))

        else:

            # key was not found - are we raising an exception?  if so, then do it!
            if (raiseExceptionIfNotFound):
                raise Exception("Could not locate key \"{0}\" in response dictionary.".format(keyName))

        # otherwise, return null.
        return None


    @staticmethod
    def GetDictKeyValueDateTime(oDict:dict, keyName:str, raiseExceptionIfNotFound:bool=False) -> datetime:
        """
        Checks a dictionary for the specified key name and returns the value if the
        key exists; otherwise, null is returned.

        Args:
            oDict (dict):
                Dictionary to check for the specified key name.
            keyName (str):
                Key name to check for.
            raiseExceptionIfNotFound (bool):
                True to raise an Exception if the specified keyName is not found in the dictionary;  
                otherwise, False.  
                Default value: False  

        Returns:
            The value of the specified key name if the key exists; otherwise, null.
        """
        # does dictionary contain the key?
        if (XPRRestServiceBase.DictHasKey(oDict, keyName)):

            value = oDict[keyName]

            # is it a datetime value? if so, then return the value.
            if (isinstance(value, datetime)):
                return value

            # is it an string value? if so, then convert it to a datetime.
            if (isinstance(value, str)):

                try:
                    return DataTypeHelper.DateTimeFromString(value, keyName, raiseExceptionIfNotFound)
                except Exception as ex:
                    return None

        else:

            # key was not found - are we raising an exception?  if so, then do it!
            if (raiseExceptionIfNotFound):
                raise Exception("Could not locate key \"{0}\" in response dictionary.".format(keyName))

        # otherwise, return null.
        return None


    def LoginBasicUser(self, username:str, password:str) -> XPRLoginInfo:
        """
        Authenticates a user with the specified Basic User login account.

        Args:
            username (str):
                Basic account type User Name to authenticate.
            password (str):
                Basic account type Password for the specified User Name to authenticate.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        Returns:
            An XPRLoginInfo class that contains Login details.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/LoginBasicUser.py
        ```
        </details>
        """
        serviceMethodName:str = "LoginBasicUser"
        loginInfo:XPRLoginInfo = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            with self._fLock:

                # trace.
                _logsi.LogMessage("Logging into XProtect REST API Gateway using Basic User credentials")

                # validations.
                if (username == None) or (len(username) == 0):
                    raise Exception(XPRAppMessages.ARGUMENT_REQUIRED_ERROR.format("userName"))
                if (password == None) or (len(password) == 0):
                    raise Exception(XPRAppMessages.ARGUMENT_REQUIRED_ERROR.format("password"))

                # from python sample project:
                # https://github.com/milestonesys/mipsdk-samples-protocol/blob/main/RestfulCommunicationPython/identity_provider.py

                # REST request example(url, headers, body):

                # POST http://myapigateway.example.com:80/api/idp/connect/token

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/x-www-form-urlencoded
 
                #grant_type=password&client_id=GrantValidatorClient&username=yourusername&password=yourpassword

                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/idp/connect/token".format(self.ApiGatewayUrlPrefix)

                reqheaders:list[str] = {
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    }

                reqbody:str = \
                    """
                    grant_type=password&client_id=GrantValidatorClient&username={username}&password={password}
                    """.format(username=parse.quote(username), 
                               password=parse.quote(password))

                # create request object.
                req:Request = Request('POST', requrl, headers=reqheaders, data=inspect.cleandoc(reqbody))

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqprep.body, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # process rest service response dictionary item node(s).
                loginInfo:XPRLoginInfo = self._Parse_Login(oDict)

                # set additional login info properties.
                loginInfo.AuthenticationType = XPRAuthenticationType.Basic
                loginInfo.UserName = username
                loginInfo.Password = password

                # trace.
                _logsi.LogObject(SILevel.Verbose, "LoginInfo object created", loginInfo, excludeNonPublic=True)

                # set internal reference.
                self._fLoginInfo = loginInfo

                # return login info to caller.
                return loginInfo

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def LoginWindowsUser(self, username:str, password:str) -> XPRLoginInfo:
        """
        Authenticates a user with the specified Windows User login account.

        Args:
            username (str):
                Windows account type User Name to authenticate.
            password (str):
                Windows account type Password for the specified User Name to authenticate.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        Returns:
            An XPRLoginInfo class that contains Login details.

        Note that the token is retrieved directly from the identity provider as MIP VMS REST API gateway 
        does not support pass-through of NTLM authentication.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/LoginWindowsUser.py
        ```
        </details>
        """
        serviceMethodName:str = "LoginWindowsUser"
        loginInfo:XPRLoginInfo = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            with self._fLock:

                # trace.
                _logsi.LogMessage("Logging into XProtect REST API Gateway using Windows User credentials")

                # validations.
                if (username == None) or (len(username) == 0):
                    raise Exception(XPRAppMessages.ARGUMENT_REQUIRED_ERROR.format("userName"))
                if (password == None) or (len(password) == 0):
                    raise Exception(XPRAppMessages.ARGUMENT_REQUIRED_ERROR.format("password"))

                # from python sample project:
                # https://github.com/milestonesys/mipsdk-samples-protocol/blob/main/RestfulCommunicationPython/identity_provider.py

                # REST request example(url, headers, body):

                # POST http://myapigateway.example.com:80/idp/connect/token

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/x-www-form-urlencoded
 
                #grant_type=windows_credentials&client_id=GrantValidatorClient

                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/idp/connect/token".format(self.ApiGatewayUrlPrefix)

                reqheaders:list[str] = {
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    }

                reqbody:str = \
                    """
                    grant_type=windows_credentials&client_id=GrantValidatorClient
                    """

                # create request object.
                req:Request = Request('POST', requrl, headers=reqheaders, data=inspect.cleandoc(reqbody), auth=HttpNtlmAuth(username, password))

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqprep.body, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # process rest service response dictionary item node(s).
                loginInfo:XPRLoginInfo = self._Parse_Login(oDict)

                # set additional login info properties.
                loginInfo.AuthenticationType = XPRAuthenticationType.Windows
                loginInfo.UserName = username
                loginInfo.Password = password

                # trace.
                _logsi.LogObject(SILevel.Verbose, "LoginInfo object created", loginInfo, excludeNonPublic=True)

                # set internal reference.
                self._fLoginInfo = loginInfo

                # return login info to caller.
                return loginInfo

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)
