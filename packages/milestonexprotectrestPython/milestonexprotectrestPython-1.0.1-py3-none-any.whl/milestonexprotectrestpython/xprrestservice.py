"""
Module: xprrestservice.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/07/11 | 1.0.0.0     | Initial Version.  

</details>
"""


# external package imports.
import _threading_local
from requests import Request, Session
from smartinspectpython.sisourceid import SISourceId
from urllib import parse

# our package imports.
from .xpranalyticsevent import XPRAnalyticsEvent
from .xprappmessages import XPRAppMessages
from .xprcamera import XPRCamera
from .xprchildsite import XPRChildSite
from .xprcollection import XPRCollection
from .xprdevicegroup import XPRDeviceGroup
from .xprdevice import XPRDevice
from .xpreventtype import XPREventType
from .xpreventtypegroup import XPREventTypeGroup
from .xprexception import XPRException
from .xprfilteroperator import XPRFilterOperator
from .xprgenericevent import XPRGenericEvent
from .xprgenericeventdatasource import XPRGenericEventDataSource
from .xprhardware import XPRHardware
from .xprinputevent import XPRInputEvent
from .xprlicensedetail import XPRLicenseDetail
from .xprlicenseinformation import XPRLicenseInformation
from .xprlicenseoverview import XPRLicenseOverview
from .xprlicenseproduct import XPRLicenseProduct
from .xprmetadata import XPRMetadata
from .xprmicrophone import XPRMicrophone
from .xprmotiondetection import XPRMotionDetection
from .xproutput import XPROutput
from .xprrecordingserver import XPRRecordingServer
from .xprrestservicebase import XPRRestServiceBase
from .xprsite import XPRSite
from .xprsiteowner import XPRSiteOwner
from .xprspeaker import XPRSpeaker
from .xprstategroup import XPRStateGroup
from .xprstream import XPRStream
from .xpruserdefinedevent import XPRUserDefinedEvent

# our package constants.
from .xprconst import (
    MSG_TRACE_PROCESSING_DICTIONARY,
    MSG_TRACE_RESULT_COLLECTION,
    MSG_TRACE_RESULT_OBJECT,
    MSG_TRACE_METHOD_RESTREQUEST,
    MSG_TRACE_METHOD_RESTREQUEST_HEADERS,
    MSG_TRACE_METHOD_RESTREQUEST_BODY
)

# get smartinspect logger reference.
from smartinspectpython.siauto import SIAuto, SISession, SILevel, SIColors
_logsi:SISession = SIAuto.Main

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPRRestService(XPRRestServiceBase):
    """
    The REST Service class provides access to XProtect API Gateway REST services.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.

        Raises:
            Exception:
                The method fails for any reason.
        """
        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            # initialize the base class.
            super().__init__()

            # trace.
            _logsi.LogObject(SILevel.Verbose, "XPRRestService Object Initialized", self)

        except Exception as ex:

            # trace.
            _logsi.LogException(None, ex)
            raise

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _GetFilterQueryString(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> str:
        """
        Parses filter criteria values, and returns a url querystring value.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            A filter criteria url querystring.

        Raises:
            Exception:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.
        """
        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 
   
            # initialize properties.
            requrl:str = ""
            requrlSep:str = "?"
            filterUrl:str = ""
            hasFilter:bool = True

            # validations.
            if (includeDisabled == None):
                includeDisabled = True
            if (filterOperator == None):
                filterOperator = XPRFilterOperator.NotSet
            if not (isinstance(filterOperator, XPRFilterOperator)):
                raise TypeError(XPRAppMessages.ARGUMENT_TYPE_ERROR.format("filterOperator", "XPRFilterOperator", type(filterOperator).__name__))
            if (filterValue) and not (isinstance(filterValue, str)):
                filterValue = str(filterValue)  # gotta convert int to str for len() check below!

            if (filterName == None) or (len(filterName) == 0):
                hasFilter = False
            if (filterOperator == None) or (filterOperator == XPRFilterOperator.NotSet):
                hasFilter = False
            if (filterValue == None) or (len(filterValue) == 0):
                hasFilter = False

            # append querystring value: disabled.
            if (includeDisabled):
                requrl = requrl + requrlSep + "disabled"
                requrlSep = "&"

            # were ALL filter criteria argumenta specified?
            if (hasFilter):

                # filter url examples:
                #  name=iPadCam01 Camera        where name is 'IPadCam01 Camera'.
                #  name=IPADCAM01 CAMERA        where name is 'IPadCam01 Camera'.
                #  name=contains:'01'           where name contains a '01'
                #  name=contains:01             where name contains a '01'
                #  description=contains:%26     where description contains an ampersand (&) character.
                #  name=beginswith:IPAD         where name begins with 'IPad'.
                #  activated=lt:3               where activated is less than 3.

                # formulate filter criteria.
                if (filterOperator == XPRFilterOperator.equals):
                    filterUrl = "{0}={1}".format(parse.quote(filterName),
                                                 parse.quote(filterValue)
                    )
                else:
                    filterUrl = "{0}={1}:{2}".format(parse.quote(filterName),
                                                     filterOperator.name,
                                                     parse.quote(filterValue)
                    )

                # append querystring value: filter.
                requrl = requrl + requrlSep + filterUrl
                requrlSep = "&"

            # return filter querystring to caller.
            return requrl

        except Exception as ex:

            raise Exception("Could not process filter arguments!", ex)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_AnalyticsEvent(self, oDict:dict, serviceMethodName:str) -> XPRAnalyticsEvent:
        """
        Parses a Analytics Event information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRAnalyticsEvent class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "AnalyticsEvent"
        oItem:XPRAnalyticsEvent = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            # {
            #   "displayName": "My Analytics Event 001",
            #   "id": "8bad255e-cd31-4e8b-8725-7be75fc1e564",
            #   "name": "My Analytics Event 001",
            #   "lastModified": "2023-09-07T12:54:41.4330000-05:00",
            #   "description": "My Analytics Event 001 description.",
            #   "sourceArray": [
            #     "Camera",
            #     "CameraGroup"
            #   ],
            #   "relations": {
            #     "self": {
            #       "type": "analyticsEvents",
            #       "id": "8bad255e-cd31-4e8b-8725-7be75fc1e564"
            #     }
            #   }
            # }
            
            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRAnalyticsEvent()
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Description = self.GetDictKeyValueString(oDict, "description")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")

                # parse array list properties.
                self.AddDictKeyValueArrayStrings(oDict, "sourceArray", oItem.SourceArray)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_Camera(self, oDict:dict, serviceMethodName:str) -> XPRCamera:
        """
        Parses a Camera information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRCamera class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "Camera"
        oItem:XPRCamera = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "iPadCam01 Camera",
            #  "enabled": true,
            #  "id": "0c60e7bf-9d57-4047-b623-e76d375a1fe6",
            #  "name": "iPadCam01 Camera",
            #  "channel": 0,
            #  "description": "IP = 192.168.1.154, port 8554\r\nLive Feed Stream = http://192.168.1.154:8554",
            #  "createdDate": "0001-01-01T00:00:00.0000000",
            #  "lastModified": "2023-08-03T02:20:21.2570000Z",
            #  "gisPoint": "POINT (-96.16593 41.27878)",
            #  "shortName": "iPadCam01",
            #  "icon": 0,
            #  "coverageDirection": "0.5",
            #  "coverageDepth": "4.57200000001829",
            #  "coverageFieldOfView": "0.25",
            #  "recordingFramerate": "5",
            #  "recordKeyframesOnly": false,
            #  "recordOnRelatedDevices": true,
            #  "recordingEnabled": true,
            #  "prebufferEnabled": true,
            #  "prebufferInMemory": true,
            #  "prebufferSeconds": 3,
            #  "edgeStorageEnabled": false,
            #  "edgeStoragePlaybackEnabled": false,
            #  "manualRecordingTimeoutEnabled": true,
            #  "manualRecordingTimeoutMinutes": 5,
            #  "recordingStorage": {
            #    "type": "storages",
            #    "id": "42dd23f1-7513-48a0-bdc3-1e26351d7cd8"
            #  },
            #  "relations": {
            #    "parent": {
            #      "type": "hardware",
            #      "id": "08cf6a24-c7ab-4b50-80e0-5a56cf624c5f"
            #    },
            #    "self": {
            #      "type": "cameras",
            #      "id": "0c60e7bf-9d57-4047-b623-e76d375a1fe6"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRCamera()
                self._Parse_Device(oDict, serviceMethodName, oItem)

                # parse device-specific properties.
                oItem.EdgeStorageEnabled = self.GetDictKeyValueBool(oDict, "edgeStorageEnabled")
                oItem.EdgeStoragePlaybackEnabled = self.GetDictKeyValueBool(oDict, "edgeStoragePlaybackEnabled")
                oItem.ManualRecordingTimeoutEnabled = self.GetDictKeyValueBool(oDict, "manualRecordingTimeoutEnabled")
                oItem.ManualRecordingTimeoutMinutes = self.GetDictKeyValueInt(oDict, "manualRecordingTimeoutMinutes")
                oItem.PrebufferEnabled = self.GetDictKeyValueBool(oDict, "prebufferEnabled")
                oItem.PrebufferInMemory = self.GetDictKeyValueBool(oDict, "prebufferInMemory")
                oItem.PrebufferSeconds = self.GetDictKeyValueInt(oDict, "prebufferSeconds")
                oItem.RecordingFramerate = self.GetDictKeyValueInt(oDict, "recordingFramerate")
                oItem.RecordKeyFramesOnly = self.GetDictKeyValueBool(oDict, "recordKeyframesOnly")
                oItem.RecordOnRelatedDevices = self.GetDictKeyValueBool(oDict, "recordOnRelatedDevices")
                oItem.RecordingEnabled = self.GetDictKeyValueBool(oDict, "recordingEnabled")

                # parse relational data.
                oItem.RecordingStorageId = self.GetParentTypeId(oDict, "recordingStorage", "storages", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_ChildSite(self, oDict:dict, serviceMethodName:str) -> XPRChildSite:
        """
        Parses a ChildSite information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetChildSites", etc.

        Returns:
            An XPRChildSite class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "ChildSite"
        oItem:XPRChildSite = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "DKTA-0508SK0025",
            #  "id": "fc9e358e-a24b-4890-9a21-958309447434",
            #  "description": "Site may have a long description",
            #  "lastModified": "2023-08-24T16:31:48.3330000Z",
            #  "connectionState": "Attached",
            #  "version": "23.2.0.1",
            #  "serviceAccount": "S-1-5-20",
            #  "synchronizationStatus": 201,
            #  "relations": {
            #    "self": {
            #      "type": "childSites",
            #      "id": "fc9e358e-a24b-4890-9a21-958309447434"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRChildSite()
                oItem.ConnectionState = self.GetDictKeyValueString(oDict, "connectionState")
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.Description = self.GetDictKeyValueString(oDict, "description")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.Name = self.GetDictKeyValueString(oDict, "displayName")   # no "name" attribute - just use "displayname" instead.
                oItem.ServiceAccount = self.GetDictKeyValueString(oDict, "serviceAccount")
                oItem.SynchronizationStatus = self.GetDictKeyValueInt(oDict, "synchronizationStatus")
                oItem.Version = self.GetDictKeyValueString(oDict, "version")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_Device(self, oDict:dict, serviceMethodName:str, oItem:XPRDevice) -> None:
        """
        Parses a Device information JSON response, loading properties of a managed class instance 
        that represent the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.
            oItem (XPRDevice):
                Object that inherits from XPRDevice base class.

        Raises:
            Exception:
                The method fails for any reason.  

        This can be used for any methods that parse properties for classes that inherit 
        from the XPRDevice base class (e.g. XPRCamera, XPRInputEvent, XPROutput,
        XPRMicrophone, XPRMetadata, XPRSpeaker).
        """
        methodKeyName:str = "Device"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "id": "0c60e7bf-9d57-4047-b623-e76d375a1fe6",
            #  "name": "iPadCam01 Camera",
            #  "channel": 0,
            #  "description": "IP = 192.168.1.154, port 8554\r\nLive Feed Stream = http://192.168.1.154:8554",
            #  "shortName": "iPadCam01",
            #  "gisPoint": "POINT (-96.16593 41.27878)",
            #  "icon": 0,
            #  "displayName": "iPadCam01 Camera",
            #  "enabled": true,
            #  "createdDate": "0001-01-01T00:00:00.0000000",
            #  "lastModified": "2023-08-03T02:20:21.2570000Z",

            #  "relations": {
            #    "parent": {
            #      "type": "hardware",
            #      "id": "08cf6a24-c7ab-4b50-80e0-5a56cf624c5f"
            #    },
            #    "self": {
            #      "type": "cameras",
            #      "id": "0c60e7bf-9d57-4047-b623-e76d375a1fe6"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem.Channel = self.GetDictKeyValueInt(oDict, "channel")
                oItem.CoverageDirection = self.GetDictKeyValueFloat(oDict, "coverageDirection")
                oItem.CoverageDepth = self.GetDictKeyValueFloat(oDict, "coverageDepth")
                oItem.CoverageFieldOfView = self.GetDictKeyValueFloat(oDict, "coverageFieldOfView")
                oItem.DateCreated = self.GetDictKeyValueDateTime(oDict, "createdDate")
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.Description = self.GetDictKeyValueString(oDict, "description")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Enabled = self.GetDictKeyValueBool(oDict, "enabled")
                oItem.GisPoint = self.GetDictKeyValueString(oDict, "gisPoint")
                oItem.Icon = self.GetDictKeyValueInt(oDict, "icon")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")
                oItem.ShortName = self.GetDictKeyValueString(oDict, "shortName")

                # parse relational data.
                oItem.HardwareId = self.GetRelationParentTypeIdHardware(oDict, serviceMethodName)

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_DeviceGroup(self, oDict:dict, serviceMethodName:str, deviceType:str) -> XPRDeviceGroup:
        """
        Parses a Device Group information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.
            deviceTypeName (str):
                Device type name this object is parsed from (e.g. "CameraGroup", "MicrophoneGroup", etc).

        Returns:
            An XPRDeviceGroup class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "DeviceGroup"
        oItem:XPRDeviceGroup = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "iPad Cameras",
            #  "id": "0275869c-808f-4387-8431-c210799e7f61",
            #  "name": "iPad Cameras",
            #  "description": "All iPad Cameras.",
            #  "lastModified": "2023-06-25T21:42:52.2130000Z",
            #  "builtIn": false,
            #  "relations": {
            #    "self": {
            #      "type": "cameraGroups",
            #      "id": "0275869c-808f-4387-8431-c210799e7f61"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRDeviceGroup()
                oItem.BuiltIn = self.GetDictKeyValueBool(oDict, "builtIn")
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.Description = self.GetDictKeyValueString(oDict, "description")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.ItemType = deviceType
                oItem.Name = self.GetDictKeyValueString(oDict, "name")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_EventType(self, oDict:dict, serviceMethodName:str) -> XPREventType:
        """
        Parses a EventType information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPREventType class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "EventType"
        oItem:XPREventType = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            # {
            #   "displayName": "Motion Stopped",
            #   "id": "6f55a7a7-d21c-4629-ac18-af1975e395a2",
            #   "name": "MotionStopped",
            #   "lastModified": "2023-06-25T21:22:20.3930000Z",
            #   "description": "",
            #   "generatorType": "RecorderPlugin",
            #   "generatorSubtype": "Server",
            #   "generatorName": "Motion Detection Plugin",
            #   "generatorID": "F020C881-72BF-4014-8504-2B4A5A658F1A",
            #   "generatorGroupName": "Analytics Events",
            #   "generatorGroupId": "a96692c8-51b1-4f87-b12c-0d3d9cbfc5a4",
            #   "occursGlobally": false,
            #   "builtIn": false,
            #   "counterEventID": "6eb95dd6-7ccc-4bce-99f8-af0d0b582d77",
            #   "sourceArray": [
            #     "Camera",
            #     "CameraGroup"
            #   ],
            #   "sourceFilterArray": [
            #     "",
            #     ""
            #   ],
            #   "stateGroupId": "720ef62a-78be-418a-8e4c-ee04ffca6429",
            #   "state": "No Motion",
            #   "relations": {
            #     "parent": {
            #       "type": "eventTypeGroups",
            #       "id": "1ae79228-ad07-4e56-be43-5ebf9b7c54a5"
            #     },
            #     "self": {
            #       "type": "eventTypes",
            #       "id": "6f55a7a7-d21c-4629-ac18-af1975e395a2"
            #     }
            #   }
            # }
                    
            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPREventType()
                oItem.BuiltIn = self.GetDictKeyValueBool(oDict, "builtIn")
                oItem.CounterEventID = self.GetDictKeyValueString(oDict, "counterEventID")
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.Description = self.GetDictKeyValueString(oDict, "description")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.GeneratorGroupId = self.GetDictKeyValueString(oDict, "generatorGroupId")
                oItem.GeneratorGroupName = self.GetDictKeyValueString(oDict, "generatorGroupName")
                oItem.GeneratorId = self.GetDictKeyValueString(oDict, "generatorID")
                oItem.GeneratorName = self.GetDictKeyValueString(oDict, "generatorName")
                oItem.GeneratorSubType = self.GetDictKeyValueString(oDict, "generatorSubtype")
                oItem.GeneratorType = self.GetDictKeyValueString(oDict, "generatorType")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")
                oItem.OccursGlobally = self.GetDictKeyValueBool(oDict, "occursGlobally")
                oItem.State = self.GetDictKeyValueString(oDict, "state")
                oItem.StateGroupId = self.GetDictKeyValueString(oDict, "stateGroupId")

                # parse array list properties.
                self.AddDictKeyValueArrayStrings(oDict, "sourceArray", oItem.SourceArray)
                self.AddDictKeyValueArrayStrings(oDict, "sourceFilterArray", oItem.SourceFilterArray)
                    
                # parse relational data.
                oItem.EventTypeGroupId = self.GetRelationParentTypeId(oDict, "parent", "eventTypeGroups", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_EventTypeGroup(self, oDict:dict, serviceMethodName:str) -> XPREventTypeGroup:
        """
        Parses a EventType Group information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPREventTypeGroup class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "EventTypeGroup"
        oItem:XPREventTypeGroup = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            # {
            #   "displayName": "Device - Predefined",
            #   "relations": {
            #     "self": {
            #       "type": "eventTypeGroups",
            #       "id": "1ae79228-ad07-4e56-be43-5ebf9b7c54a5"
            #     }
            #   }
            # }
    
            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPREventTypeGroup()
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")

                # parse relational data.
                oItem.Id = self.GetRelationParentTypeId(oDict, "self", "eventTypeGroups", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_GenericEvent(self, oDict:dict, serviceMethodName:str) -> XPRGenericEvent:
        """
        Parses a Generic Event information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRGenericEvent class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "GenericEvent"
        oItem:XPRGenericEvent = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            # {
            #   "displayName": "My Generic Event 001",
            #   "enabled": true,
            #   "id": "4d9d1dc5-85dd-4c8e-bcfe-d6b90573dd1f",
            #   "name": "My Generic Event 001",
            #   "dataSource": "genericEventDataSources/b867db0c-be9e-422b-b934-6fc7fa98c5d8",
            #   "expression": "\"a\" AND (\"b\" OR \"c\")",
            #   "expressionType": "0",
            #   "priority": 69,
            #   "lastModified": "2023-09-07T12:55:54.3970000-05:00",
            #   "relations": {
            #     "self": {
            #       "type": "genericEvents",
            #       "id": "4d9d1dc5-85dd-4c8e-bcfe-d6b90573dd1f"
            #     }
            #   }
            # }
            
            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRGenericEvent()
                oItem.DataSource = self.GetDictKeyValueString(oDict, "dataSource")
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Enabled = self.GetDictKeyValueBool(oDict, "enabled")
                oItem.Expression = self.GetDictKeyValueString(oDict, "expression")
                oItem.ExpressionType = self.GetDictKeyValueString(oDict, "expressionType")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")
                oItem.Priority = self.GetDictKeyValueInt(oDict, "priority")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)



    def _Parse_GenericEventDataSource(self, oDict:dict, serviceMethodName:str) -> XPRGenericEventDataSource:
        """
        Parses a Generic Event DataSource information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRGenericEventDataSource class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "GenericEventDataSource"
        oItem:XPRGenericEventDataSource = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            # {
            #   "displayName": "MyDataSource01",
            #   "enabled": true,
            #   "id": "15a1ee5e-bc4a-4d91-b03b-fb11dff502c6",
            #   "name": "MyDataSource01",
            #   "dataSourcePort": 1238,
            #   "dataSourceSeparator": "13,10",
            #   "dataSourceEncoding": 20127,
            #   "dataSourceLog": false,
            #   "dataSourceEcho": "None",
            #   "dataSourceAllowed": "192.168.1.1;\n192.168.1.2;\n192.168.1.3",
            #   "dataSourceAllowed6": "fe80::8267:3a69:65a:28d6;\r\nfe80::8267:3a69:71b:39e7",
            #   "dataSourceProtocol": "Udp",
            #   "dataSourceAddressFamily": "Both",
            #   "relations": {
            #     "self": {
            #       "type": "genericEventDataSources",
            #       "id": "15a1ee5e-bc4a-4d91-b03b-fb11dff502c6"
            #     }
            #   }
            # }
                
            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRGenericEventDataSource()
                oItem.DataSourceAddressFamily = self.GetDictKeyValueString(oDict, "dataSourceAddressFamily")
                oItem.DataSourceAllowedIpv4 = self.GetDictKeyValueString(oDict, "dataSourceAllowed")
                oItem.DataSourceAllowedIpv6 = self.GetDictKeyValueString(oDict, "dataSourceAllowed6")
                oItem.DataSourceEcho = self.GetDictKeyValueString(oDict, "dataSourceEcho")
                oItem.DataSourceEncoding = self.GetDictKeyValueInt(oDict, "dataSourceEncoding")
                oItem.DataSourceLog = self.GetDictKeyValueBool(oDict, "dataSourceLog")
                oItem.DataSourcePort = self.GetDictKeyValueInt(oDict, "dataSourcePort")
                oItem.DataSourceProtocol = self.GetDictKeyValueString(oDict, "dataSourceProtocol")
                oItem.DataSourceSeparator = self.GetDictKeyValueString(oDict, "dataSourceSeparator")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Enabled = self.GetDictKeyValueBool(oDict, "enabled")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_Hardware(self, oDict:dict, serviceMethodName:str) -> XPRHardware:
        """
        Parses a Hardware information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRHardware class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "Hardware"
        oItem:XPRHardware = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "iPadCam01",
            #  "enabled": true,
            #  "id": "08cf6a24-c7ab-4b50-80e0-5a56cf624c5f",
            #  "name": "iPadCam01",
            #  "description": "iPad Camera and Microphone via LiveReporter RTSP Streaming.\r\nIP = 192.168.1.154, port 8554\r\nLive Feed Stream = http://192.168.1.154:8554",
            #  "address": "http://192.168.1.154:8554/",
            #  "userName": "ipadcam",
            #  "model": "Universal1ChAdv",
            #  "passwordLastModified": "0001-01-01T00:00:00.0000000",
            #  "lastModified": "2023-08-29T19:10:05.8970000Z",

            #  "hardwareDriverPath": {
            #    "type": "hardwareDrivers",
            #    "id": "ab537f0c-373c-4a3c-a45f-cb0c07fc07b3"
            #  },
            #  "relations": {
            #    "parent": {
            #      "type": "recordingServers",
            #      "id": "19f94d50-b5ad-4e90-8b3f-9928bb60f9f2"
            #    },
            #    "self": {
            #      "type": "hardware",
            #      "id": "08cf6a24-c7ab-4b50-80e0-5a56cf624c5f"
            #    }
            #  }
            #},

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRHardware()
                oItem.Address = self.GetDictKeyValueString(oDict, "address")
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.Description = self.GetDictKeyValueString(oDict, "description")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Enabled = self.GetDictKeyValueBool(oDict, "enabled")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")
                oItem.Model = self.GetDictKeyValueString(oDict, "model")
                oItem.PasswordLastModified = self.GetDictKeyValueDateTime(oDict, "passwordLastModified")
                oItem.UserName = self.GetDictKeyValueString(oDict, "userName")

                # parse relational data.
                oItem.HardwareDriverId = self.GetParentTypeId(oDict, "hardwareDriverPath", "hardwareDrivers", serviceMethodName)
                oItem.RecordingServerId = self.GetRelationParentTypeId(oDict, "parent", "recordingServers", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_InputEvent(self, oDict:dict, serviceMethodName:str) -> XPRInputEvent:
        """
        Parses a InputEvent information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRInputEvent class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "InputEvent"
        oItem:XPRInputEvent = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "Test Driver Input 1",
            #  "enabled": true,
            #  "id": "1ee97b92-664b-4841-860a-b9d53b158d00",
            #  "name": "Test Driver Input 1",
            #  "channel": 0,
            #  "description": "InputEvent may have a long description",
            #  "createdDate": "2022-05-23T09:24:58.9130000+02:00",
            #  "lastModified": "2022-05-23T09:24:58.9130000+02:00",
            #  "gisPoint": "POINT EMPTY",
            #  "shortName": "string",
            #  "icon": 0,
            #  "coverageDirection": 0,
            #  "coverageDepth": 0,
            #  "coverageFieldOfView": 0,
            #  "relations": {
            #    "self": {
            #      "type": "inputEvents",
            #      "id": "1ee97b92-664b-4841-860a-b9d53b158d00"
            #    },
            #    "parent": {
            #      "type": "hardware",
            #      "id": "965c4a97-449a-4b4b-b772-e50e7b44f700"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRInputEvent()
                self._Parse_Device(oDict, serviceMethodName, oItem)

                # parse device-specific properties.
                # nothing to do here, as all properties are in the base device.

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_LicenseDetail(self, oDict:dict, serviceMethodName:str) -> XPRLicenseDetail:
        """
        Parses a LicenseDetail information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetLicenseDetails", etc.

        Returns:
            An XPRLicenseDetail class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "LicenseDetail"
        oItem:XPRLicenseDetail = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "Device License",
            #  "pluginId": "00000000-0000-0000-0000-000000000000",
            #  "licenseType": "Device License",
            #  "activated": "3",
            #  "changesWithoutActivation": "0 out of 2",
            #  "inGrace": 0,
            #  "graceExpired": "0",
            #  "notLicensed": "0",
            #  "note": ""
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRLicenseDetail()
                oItem.Activated = self.GetDictKeyValueInt(oDict, "activated")
                oItem.ChangesWithoutActivation = self.GetDictKeyValueString(oDict, "changesWithoutActivation")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.GracePeriodExpired = self.GetDictKeyValueInt(oDict, "graceExpired")
                oItem.GracePeriodIn = self.GetDictKeyValueInt(oDict, "inGrace")
                oItem.LicenseType = self.GetDictKeyValueString(oDict, "licenseType")
                oItem.NotLicensed = self.GetDictKeyValueInt(oDict, "notLicensed")
                oItem.Note = self.GetDictKeyValueString(oDict, "note")
                oItem.PluginId = self.GetDictKeyValueString(oDict, "pluginId")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_LicenseInformation(self, oDict:dict, serviceMethodName:str) -> XPRLicenseInformation:
        """
        Parses a LicenseInformation information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetLicenseInformations", etc.

        Returns:
            An XPRLicenseInformation class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "LicenseInformation"
        oItem:XPRLicenseInformation = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "XProtect Essential+ 2023 R2",
            #  "slc": "M01-C07-232-01-6C4B9A",
            #  "sku": "XPESPLUS",
            #  "careLevel": "Basic",
            #  "careId": "",
            #  "activationAutomatic": false,
            #  "relations": {
            #    "self": {
            #      "type": "licenseInformations",
            #      "id": "fc9e48ce-a39b-4327-8b92-32b012688944"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRLicenseInformation()
                oItem.ActivationAutomatic = self.GetDictKeyValueBool(oDict, "activationAutomatic")
                oItem.CareLevel = self.GetDictKeyValueString(oDict, "careLevel")
                oItem.CareId = self.GetDictKeyValueString(oDict, "careId")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.SoftwareLicenseCode = self.GetDictKeyValueString(oDict, "slc")
                oItem.Sku = self.GetDictKeyValueString(oDict, "sku")

                # parse relational data.
                oItem.Id = self.GetRelationParentTypeId(oDict, "self", "licenseInformations", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_LicenseOverview(self, oDict:dict, serviceMethodName:str) -> XPRLicenseOverview:
        """
        Parses a LicenseOverview information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetLicenseOverviews", etc.

        Returns:
            An XPRLicenseOverview class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "LicenseOverview"
        oItem:XPRLicenseOverview = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "Device License",
            #  "pluginId": "00000000-0000-0000-0000-000000000000",
            #  "licenseType": "Device License",
            #  "activated": "3 out of 8"
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRLicenseOverview()
                oItem.ActivatedStatus = self.GetDictKeyValueString(oDict, "activated")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.LicenseType = self.GetDictKeyValueString(oDict, "licenseType")
                oItem.PluginId = self.GetDictKeyValueString(oDict, "pluginId")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_LicenseProduct(self, oDict:dict, serviceMethodName:str) -> XPRLicenseProduct:
        """
        Parses a LicenseProduct information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetLicenseProducts", etc.

        Returns:
            An XPRLicenseProduct class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "LicenseProduct"
        oItem:XPRLicenseProduct = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "XProtect Essential+ 2023 R2",
            #  "productDisplayName": "XProtect Essential+ 2023 R2",
            #  "pluginId": "00000000-0000-0000-0000-000000000000",
            #  "slc": "M01-C07-232-01-6C4B9A",
            #  "expirationDate": "Unrestricted",
            #  "carePlus": "N/A",
            #  "carePremium": "N/A"
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRLicenseProduct()
                oItem.CarePlus = self.GetDictKeyValueString(oDict, "carePlus")
                oItem.CarePremium = self.GetDictKeyValueString(oDict, "carePremium")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.ExpirationDate = self.GetDictKeyValueString(oDict, "expirationDate")  # string format - could be "unrestricted"
                oItem.PluginId = self.GetDictKeyValueString(oDict, "pluginId")
                oItem.ProductDisplayName = self.GetDictKeyValueString(oDict, "productDisplayName")
                oItem.SoftwareLicenseCode = self.GetDictKeyValueString(oDict, "slc")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_Metadata(self, oDict:dict, serviceMethodName:str) -> XPRMetadata:
        """
        Parses a Metadata information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRMetadata class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "Metadata"
        oItem:XPRMetadata = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "enabled": true,
            #  "displayName": "Test Driver Metadata 1",
            #  "id": "5eb4ff4a-d570-4440-91a8-faee8b1ba205",
            #  "name": "Test Driver Metadata 1",
            #  "channel": 0,
            #  "description": "Metadata may have a long description",
            #  "createdDate": "2022-05-23T09:24:58.9130000+02:00",
            #  "lastModified": "2022-05-23T09:24:58.9130000+02:00",
            #  "gisPoint": "POINT EMPTY",
            #  "shortName": "string",
            #  "icon": 0,
            #  "coverageDirection": 0,
            #  "coverageDepth": 0,
            #  "coverageFieldOfView": 0,
            #  "recordingEnabled": true,
            #  "prebufferEnabled": true,
            #  "prebufferInMemory": true,
            #  "prebufferSeconds": 3,
            #  "edgeStorageEnabled": false,
            #  "edgeStoragePlaybackEnabled": false,
            #  "manualRecordingTimeoutEnabled": true,
            #  "manualRecordingTimeoutMinutes": 5,
            #  "recordingStorage": {
            #    "type": "storages",
            #    "id": "2f947aeb-c59d-4ea6-9586-c4cf72e3f477"
            #  },
            #  "relations": {
            #    "self": {
            #      "type": "metadata",
            #      "id": "5eb4ff4a-d570-4440-91a8-faee8b1ba205"
            #    },
            #    "parent": {
            #      "type": "hardware",
            #      "id": "965c4a97-449a-4b4b-b772-e50e7b44f700"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRMetadata()
                self._Parse_Device(oDict, serviceMethodName, oItem)

                # parse device-specific properties.
                oItem.EdgeStorageEnabled = self.GetDictKeyValueBool(oDict, "edgeStorageEnabled")
                oItem.EdgeStoragePlaybackEnabled = self.GetDictKeyValueBool(oDict, "edgeStoragePlaybackEnabled")
                oItem.ManualRecordingTimeoutEnabled = self.GetDictKeyValueBool(oDict, "manualRecordingTimeoutEnabled")
                oItem.ManualRecordingTimeoutMinutes = self.GetDictKeyValueInt(oDict, "manualRecordingTimeoutMinutes")
                oItem.PrebufferEnabled = self.GetDictKeyValueBool(oDict, "prebufferEnabled")
                oItem.PrebufferInMemory = self.GetDictKeyValueBool(oDict, "prebufferInMemory")
                oItem.PrebufferSeconds = self.GetDictKeyValueInt(oDict, "prebufferSeconds")
                oItem.RecordingEnabled = self.GetDictKeyValueBool(oDict, "recordingEnabled")

                # parse relational data.
                oItem.RecordingStorageId = self.GetParentTypeId(oDict, "recordingStorage", "storages", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_Microphone(self, oDict:dict, serviceMethodName:str) -> XPRMicrophone:
        """
        Parses a Microphone information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRMicrophone class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "Microphone"
        oItem:XPRMicrophone = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "iPadCam01 Microphone",
            #  "enabled": true,
            #  "id": "8a381bcc-7752-45dd-91f2-3aa8345d37db",
            #  "name": "iPadCam01 Microphone",
            #  "channel": 0,
            #  "description": "iPad Camera 01 Microphone.",
            #  "createdDate": "0001-01-01T00:00:00.0000000",
            #  "lastModified": "2023-07-31T22:42:10.9470000Z",
            #  "gisPoint": "POINT (151.2151 -33.8569)",
            #  "shortName": "iPadCam01 Mic",
            #  "icon": 0,
            #  "coverageDirection": "0",
            #  "coverageDepth": "0",
            #  "coverageFieldOfView": "0",
            #  "recordingEnabled": true,
            #  "prebufferEnabled": true,
            #  "prebufferInMemory": true,
            #  "prebufferSeconds": 3,
            #  "edgeStorageEnabled": false,
            #  "edgeStoragePlaybackEnabled": false,
            #  "manualRecordingTimeoutEnabled": true,
            #  "manualRecordingTimeoutMinutes": 5,
            #  "recordingStorage": {
            #    "type": "storages",
            #    "id": "42dd23f1-7513-48a0-bdc3-1e26351d7cd8"
            #  },
            #  "relations": {
            #    "parent": {
            #      "type": "hardware",
            #      "id": "08cf6a24-c7ab-4b50-80e0-5a56cf624c5f"
            #    },
            #    "self": {
            #      "type": "microphones",
            #      "id": "8a381bcc-7752-45dd-91f2-3aa8345d37db"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRMicrophone()
                self._Parse_Device(oDict, serviceMethodName, oItem)

                # parse device-specific properties.
                oItem.EdgeStorageEnabled = self.GetDictKeyValueBool(oDict, "edgeStorageEnabled")
                oItem.EdgeStoragePlaybackEnabled = self.GetDictKeyValueBool(oDict, "edgeStoragePlaybackEnabled")
                oItem.ManualRecordingTimeoutEnabled = self.GetDictKeyValueBool(oDict, "manualRecordingTimeoutEnabled")
                oItem.ManualRecordingTimeoutMinutes = self.GetDictKeyValueInt(oDict, "manualRecordingTimeoutMinutes")
                oItem.PrebufferEnabled = self.GetDictKeyValueBool(oDict, "prebufferEnabled")
                oItem.PrebufferInMemory = self.GetDictKeyValueBool(oDict, "prebufferInMemory")
                oItem.PrebufferSeconds = self.GetDictKeyValueInt(oDict, "prebufferSeconds")
                oItem.RecordingEnabled = self.GetDictKeyValueBool(oDict, "recordingEnabled")

                # parse relational data.
                oItem.RecordingStorageId = self.GetParentTypeId(oDict, "recordingStorage", "storages", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_MotionDetection(self, oDict:dict, serviceMethodName:str, parentType:str) -> XPRMotionDetection:
        """
        Parses a MotionDetection information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameraMotionDetections", etc.
            parentType (str):
                Type name of the parent owner ("cameras", etc).

        Returns:
            An XPRMotionDetection class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "MotionDetection"
        oItem:XPRMotionDetection = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "Motion detection",
            #  "enabled": true,
            #  "id": "f0f31f69-36a2-46a3-80b6-48e4bf617db8",
            #  "manualSensitivityEnabled": false,
            #  "manualSensitivity": 100,
            #  "threshold": 2000,
            #  "keyframesOnly": true,
            #  "processTime": "Ms500",
            #  "detectionMethod": "Fast",
            #  "generateMotionMetadata": true,
            #  "useExcludeRegions": true,
            #  "gridSize": "Grid16X16",
            #  "excludeRegions": "0000000000000001000000000000000100000000000000010000000000000001000000000000000100000000000000010000000000000001000000000000000100000000000000010000000000000001000000000000000100000000000000010000000000000001000000000000000100000000000000010000000000011111",
            #  "hardwareAccelerationMode": "Automatic",
            #  "relations": {
            #    "parent": {
            #      "type": "cameras",
            #      "id": "f0f31f69-36a2-46a3-80b6-48e4bf617db8"
            #    },
            #    "self": {
            #      "type": "motionDetections",
            #      "id": "f0f31f69-36a2-46a3-80b6-48e4bf617db8"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRMotionDetection()
                oItem.DetectionMethod = self.GetDictKeyValueString(oDict, "detectionMethod")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Enabled = self.GetDictKeyValueBool(oDict, "enabled")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.ExcludeRegions = self.GetDictKeyValueString(oDict, "excludeRegions")
                oItem.GenerateMotionMetadata = self.GetDictKeyValueBool(oDict, "generateMotionMetadata")
                oItem.GridSize = self.GetDictKeyValueString(oDict, "gridSize")
                oItem.HardwareAccelerationMode = self.GetDictKeyValueString(oDict, "hardwareAccelerationMode")
                oItem.KeyframesOnly = self.GetDictKeyValueBool(oDict, "keyframesOnly")
                oItem.ManualSensitivity = self.GetDictKeyValueInt(oDict, "manualSensitivity")
                oItem.ManualSensitivityEnabled = self.GetDictKeyValueBool(oDict, "manualSensitivityEnabled")
                oItem.ProcessTime = self.GetDictKeyValueString(oDict, "processTime")
                oItem.Threshold = self.GetDictKeyValueInt(oDict, "threshold")
                oItem.UseExcludeRegions = self.GetDictKeyValueBool(oDict, "useExcludeRegions")

                # parse relational data.
                oItem.ParentType = parentType
                oItem.ParentId = self.GetRelationParentTypeId(oDict, "parent", parentType, serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

                #raise Exception("** TEST TODO _Parse_MotionDetection exception.")

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_Output(self, oDict:dict, serviceMethodName:str) -> XPROutput:
        """
        Parses a Output information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPROutput class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "Output"
        oItem:XPROutput = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "Drift Race Output",
            #  "enabled": true,
            #  "id": "2d6e053a-6e1b-462b-81ec-a2c3d54148c0",
            #  "name": "Drift Race Output",
            #  "channel": 0,
            #  "description": "Output may have a long description",
            #  "createdDate": "2022-05-23T09:24:58.9130000+02:00",
            #  "lastModified": "2022-05-23T09:24:58.9130000+02:00",
            #  "gisPoint": "POINT EMPTY",
            #  "shortName": "string",
            #  "icon": 0,
            #  "coverageDirection": 0,
            #  "coverageDepth": 0,
            #  "coverageFieldOfView": 0,
            #  "relations": {
            #    "self": {
            #      "type": "outputs",
            #      "id": "2d6e053a-6e1b-462b-81ec-a2c3d54148c0"
            #    },
            #    "parent": {
            #      "type": "hardware",
            #      "id": "965c4a97-449a-4b4b-b772-e50e7b44f700"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPROutput()
                self._Parse_Device(oDict, serviceMethodName, oItem)

                # parse device-specific properties.
                # nothing to do here, as all properties are in the base device.

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_RecordingServer(self, oDict:dict, serviceMethodName:str) -> XPRRecordingServer:
        """
        Parses a RecordingServer information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetRecordingServers", etc.

        Returns:
            An XPRRecordingServer class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "RecordingServer"
        oItem:XPRRecordingServer = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "WIN10VM",
            #  "enabled": true,
            #  "id": "19f94d50-b5ad-4e90-8b3f-9928bb60f9f2",
            #  "name": "WIN10VM",
            #  "description": "XProtect Recording Server WIN10VM.",
            #  "lastModified": "2023-08-09T04:26:37.4530000Z",
            #  "synchronizationTime": -1,
            #  "timeZoneName": "Central Standard Time",
            #  "hostName": "win10vm",
            #  "portNumber": 7563,
            #  "webServerUri": "http://win10vm:7563/",
            #  "activeWebServerUri": "",
            #  "publicAccessEnabled": false,
            #  "publicWebserverHostName": "",
            #  "publicWebserverPort": 0,
            #  "multicastServerAddress": "0.0.0.0",
            #  "shutdownOnStorageFailure": false,
            #  "relations": {
            #    "parent": {
            #      "type": "sites",
            #      "id": "fc9e48ce-a39b-4327-8b92-32b012688944"
            #    },
            #    "self": {
            #      "type": "recordingServers",
            #      "id": "19f94d50-b5ad-4e90-8b3f-9928bb60f9f2"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRRecordingServer()
                oItem.ActiveWebServerUri = self.GetDictKeyValueString(oDict, "activeWebServerUri")
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.Description = self.GetDictKeyValueString(oDict, "description")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Enabled = self.GetDictKeyValueBool(oDict, "enabled")
                oItem.HostName = self.GetDictKeyValueString(oDict, "hostName")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.MulticastServerAddress = self.GetDictKeyValueString(oDict, "multicastServerAddress")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")
                oItem.PortNumber = self.GetDictKeyValueInt(oDict, "portNumber")
                oItem.PublicAccessEnabled = self.GetDictKeyValueBool(oDict, "publicAccessEnabled")
                oItem.PublicWebserverHostName = self.GetDictKeyValueString(oDict, "publicWebserverHostName")
                oItem.PublicWebserverPort = self.GetDictKeyValueInt(oDict, "publicWebserverPort")
                oItem.ShutdownOnStorageFailure = self.GetDictKeyValueBool(oDict, "shutdownOnStorageFailure")
                oItem.SynchronizationTime = self.GetDictKeyValueInt(oDict, "synchronizationTime")
                oItem.TimeZoneName = self.GetDictKeyValueString(oDict, "timeZoneName")
                oItem.WebServerUri = self.GetDictKeyValueString(oDict, "webServerUri")

                # parse relational data.
                oItem.SiteId = self.GetRelationParentTypeId(oDict, "parent", "sites", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_Site(self, oDict:dict, serviceMethodName:str) -> XPRSite:
        """
        Parses a Site information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetSites", etc.

        Returns:
            An XPRSite class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "Site"
        oItem:XPRSite = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "WIN10VM",
            #  "id": "fc9e48ce-a39b-4327-8b92-32b012688944",
            #  "name": "WIN10VM",
            #  "description": "",
            #  "lastModified": "2023-08-24T16:31:48.3330000Z",
            #  "timeZone": "Central Standard Time",
            #  "computerName": "WIN10VM",
            #  "domainName": "",
            #  "lastStatusHandshake": "2023-08-24T16:31:48.3330000Z",
            #  "physicalMemory": 0,
            #  "platform": "[Not Available]",
            #  "processors": 0,
            #  "serviceAccount": "S-1-5-20",
            #  "synchronizationStatus": 0,
            #  "masterSiteAddress": "",
            #  "version": "23.2.0.1",
            #  "relations": {
            #    "self": {
            #      "type": "sites",
            #      "id": "fc9e48ce-a39b-4327-8b92-32b012688944"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRSite()
                oItem.ComputerName = self.GetDictKeyValueString(oDict, "computerName")
                oItem.DateLastStatusHandshake = self.GetDictKeyValueDateTime(oDict, "lastStatusHandshake")
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.Description = self.GetDictKeyValueString(oDict, "description")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.DomainName = self.GetDictKeyValueString(oDict, "domainName")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")
                oItem.MasterSiteAddress = self.GetDictKeyValueString(oDict, "masterSiteAddress")
                oItem.PhysicalMemory = self.GetDictKeyValueInt(oDict, "physicalMemory")
                oItem.Platform = self.GetDictKeyValueString(oDict, "platform")
                oItem.Processors = self.GetDictKeyValueInt(oDict, "processors")
                oItem.ServiceAccount = self.GetDictKeyValueString(oDict, "serviceAccount")
                oItem.SynchronizationStatus = self.GetDictKeyValueInt(oDict, "synchronizationStatus")
                oItem.TimeZoneName = self.GetDictKeyValueString(oDict, "timeZone")
                oItem.Version = self.GetDictKeyValueString(oDict, "version")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_SiteOwner(self, oDict:dict, serviceMethodName:str) -> XPRSiteOwner:
        """
        Parses a SiteOwner information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetSiteOwners", etc.

        Returns:
            An XPRSiteOwner class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "SiteOwner"
        oItem:XPRSiteOwner = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "Basic Information",
            #  "[43e367b7-fa73-4945-99ae-8b66769b03e2]/address.Email": "JohnSmith@yahoo.com",
            #  "[275be5c9-6bbb-485f-bab9-fab67afd4f55]/address.Address": "123 Main Street",
            #  "[658a2c5b-86e7-4f46-9b81-b343c112b0a9]/address.State": "NE",
            #  "[bc772586-53ea-461e-aab2-d96b2c6dd437]/address.ZipCode": "68123",
            #  "[69f82588-1862-4d39-8f2a-3ae2ec89c0ef]/address.Country": "USA",
            #  "[4f682bb5-da42-4f52-a09f-8dd45b3c3f6f]/address.Phone": "888-555-1234",
            #  "[efaedd38-9f12-4f9f-b4c4-89a5d0337434]/address.Email": "Anotheremail@domain.com",
            #  "[e2ce2431-4b6a-4324-a3b3-09243ff53f15]/admin.Name": "John Smith",
            #  "[8de36344-5dcc-440a-91bd-be011aa34a5f]/admin.Email": "JohnSmith@yahoo.com",
            #  "[4aa49202-124b-491f-bd39-0826fd9ae61d]/admin.Phone": "888-555-5678",
            #  "[911f13cd-9fb9-4b63-ba32-4a341153a4d5]/additional.AdditionalInfo": "Additional info - home surveillance system.",
            #  "[b0b199c3-6981-49a2-be35-86231bca8502]/additional.AdditionalInfo": "Additional info - line 2",
            #  "relations": {
            #    "self": {
            #      "type": "owner",
            #      "id": "fc9e48ce-a39b-4327-8b92-32b012688944"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRSiteOwner()
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")

                # the XProtect UI allows multiple entries for each property.  if a value has already been assigned
                # to a property, then we will append a delimiter (e.g. ",", CRLF, etc) before adding the next value.

                # process all keys in the dictionary.
                # we have to do it this way, as the REST api response contains a GUID prefix for the key name.
                # example:  "[43e367b7-fa73-4945-99ae-8b66769b03e2]/address.Email": "siteadmin@domain.com"

                keyName:str = ""
                DLM_COMMA:str = ", "
                DLM_CRLF:str = '\n'
                for key in oDict.keys():

                    # convert key name to lower-case for faster comparison.
                    keyName = key.lower()

                    if (keyName.endswith("/additional.additionalinfo")):
                        if (oItem.AdditionalInformation) and (len(oItem.AdditionalInformation) > 0):
                            oItem.AdditionalInformation = oItem.AdditionalInformation + DLM_CRLF + oDict[key]
                        else:
                            oItem.AdditionalInformation = oDict[key]

                    if (keyName.endswith("/address.country")):
                        if (oItem.LocationCountry) and (len(oItem.LocationCountry) > 0):
                            oItem.LocationCountry = oItem.LocationCountry + DLM_COMMA + oDict[key]
                        else:
                            oItem.LocationCountry = oDict[key]

                    if (keyName.endswith("/address.email")):
                        if (oItem.LocationEMail) and (len(oItem.LocationEMail) > 0):
                            oItem.LocationEMail = oItem.LocationEMail + DLM_COMMA + oDict[key]
                        else:
                            oItem.LocationEMail = oDict[key]

                    if (keyName.endswith("/address.phone")):
                        if (oItem.LocationPhone) and (len(oItem.LocationPhone) > 0):
                            oItem.LocationPhone = oItem.LocationPhone + DLM_COMMA + oDict[key]
                        else:
                            oItem.LocationPhone = oDict[key]

                    if (keyName.endswith("/address.state")):
                        if (oItem.LocationStateProvince) and (len(oItem.LocationStateProvince) > 0):
                            oItem.LocationStateProvince = oItem.LocationStateProvince + DLM_COMMA + oDict[key]
                        else:
                            oItem.LocationStateProvince = oDict[key]

                    if (keyName.endswith("/address.address")):
                        if (oItem.LocationStreet) and (len(oItem.LocationStreet) > 0):
                            oItem.LocationStreet = oItem.LocationStreet + DLM_COMMA + oDict[key]
                        else:
                            oItem.LocationStreet = oDict[key]

                    if (keyName.endswith("/address.zipcode")):
                        if (oItem.LocationZipCode) and (len(oItem.LocationZipCode) > 0):
                            oItem.LocationZipCode = oItem.LocationZipCode + DLM_COMMA + oDict[key]
                        else:
                            oItem.LocationZipCode = oDict[key]

                    if (keyName.endswith("/admin.email")):
                        if (oItem.AdminEMail) and (len(oItem.AdminEMail) > 0):
                            oItem.AdminEMail = oItem.AdminEMail + DLM_COMMA + oDict[key]
                        else:
                            oItem.AdminEMail = oDict[key]

                    if (keyName.endswith("/admin.name")):
                        if (oItem.AdminName) and (len(oItem.AdminName) > 0):
                            oItem.AdminName = oItem.AdminName + DLM_COMMA + oDict[key]
                        else:
                            oItem.AdminName = oDict[key]

                    if (keyName.endswith("/admin.phone")):
                        if (oItem.AdminPhone) and (len(oItem.AdminPhone) > 0):
                            oItem.AdminPhone = oItem.AdminPhone + DLM_COMMA + oDict[key]
                        else:
                            oItem.AdminPhone = oDict[key]

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_Speaker(self, oDict:dict, serviceMethodName:str) -> XPRSpeaker:
        """
        Parses a Speaker information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRSpeaker class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "Speaker"
        oItem:XPRSpeaker = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "iPadCam01 Speaker",
            #  "enabled": true,
            #  "id": "8a381bcc-7752-45dd-91f2-3aa8345d37db",
            #  "name": "iPadCam01 Speaker",
            #  "channel": 0,
            #  "description": "iPad Camera 01 Speaker.",
            #  "createdDate": "0001-01-01T00:00:00.0000000",
            #  "lastModified": "2023-07-31T22:42:10.9470000Z",
            #  "gisPoint": "POINT (151.2151 -33.8569)",
            #  "shortName": "iPadCam01 Mic",
            #  "icon": 0,
            #  "coverageDirection": "0",
            #  "coverageDepth": "0",
            #  "coverageFieldOfView": "0",
            #  "recordingEnabled": true,
            #  "prebufferEnabled": true,
            #  "prebufferInMemory": true,
            #  "prebufferSeconds": 3,
            #  "edgeStorageEnabled": false,
            #  "edgeStoragePlaybackEnabled": false,
            #  "manualRecordingTimeoutEnabled": true,
            #  "manualRecordingTimeoutMinutes": 5,
            #  "recordingStorage": {
            #    "type": "storages",
            #    "id": "42dd23f1-7513-48a0-bdc3-1e26351d7cd8"
            #  },
            #  "relations": {
            #    "parent": {
            #      "type": "hardware",
            #      "id": "08cf6a24-c7ab-4b50-80e0-5a56cf624c5f"
            #    },
            #    "self": {
            #      "type": "Speakers",
            #      "id": "8a381bcc-7752-45dd-91f2-3aa8345d37db"
            #    }
            #  }
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRSpeaker()
                self._Parse_Device(oDict, serviceMethodName, oItem)

                # parse device-specific properties.
                oItem.EdgeStorageEnabled = self.GetDictKeyValueBool(oDict, "edgeStorageEnabled")
                oItem.EdgeStoragePlaybackEnabled = self.GetDictKeyValueBool(oDict, "edgeStoragePlaybackEnabled")
                oItem.ManualRecordingTimeoutEnabled = self.GetDictKeyValueBool(oDict, "manualRecordingTimeoutEnabled")
                oItem.ManualRecordingTimeoutMinutes = self.GetDictKeyValueInt(oDict, "manualRecordingTimeoutMinutes")
                oItem.PrebufferEnabled = self.GetDictKeyValueBool(oDict, "prebufferEnabled")
                oItem.PrebufferInMemory = self.GetDictKeyValueBool(oDict, "prebufferInMemory")
                oItem.PrebufferSeconds = self.GetDictKeyValueInt(oDict, "prebufferSeconds")
                oItem.RecordingEnabled = self.GetDictKeyValueBool(oDict, "recordingEnabled")

                # parse relational data.
                oItem.RecordingStorageId = self.GetParentTypeId(oDict, "recordingStorage", "storages", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_StateGroup(self, oDict:dict, serviceMethodName:str) -> XPRStateGroup:
        """
        Parses a StateGroup information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRStateGroup class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "StateGroup"
        oItem:XPRStateGroup = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            # {
            #   "displayName": "CPU usage",
            #   "name": "CPU usage",
            #   "lastModified": "2023-06-25T21:22:20.6230000Z",
            #   "states": [
            #     "Normal",
            #     "Warning",
            #     "Critical",
            #     "Undefined"
            #   ],
            #   "relations": {
            #     "self": {
            #       "type": "stateGroups",
            #       "id": "8c958201-aa02-40cf-a643-fa7f91d0bed2"
            #     }
            #   }
                  
            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRStateGroup()
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")

                # parse array list properties.
                self.AddDictKeyValueArrayStrings(oDict, "states", oItem.States)

                # parse relational data.
                oItem.Id = self.GetRelationParentTypeId(oDict, "self", "stateGroups", serviceMethodName)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_Stream(self, oDict:dict, serviceMethodName:str, parentId:str, parentType:str) -> XPRStream:
        """
        Parses a Stream information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameraStreams", etc.
            parentId (str):
                Globally unique identifier of the parent owner.
            parentType (str):
                Type name of the parent owner ("cameras", etc).

        Returns:
            An XPRStream class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "Stream"
        oItem:XPRStream = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #{
            #  "displayName": "Streams",
            #  "stream": [
            #    {
            #      "displayName": "Video stream 1",
            #      "name": "Video stream 1",
            #      "streamReferenceId": "28DC44C3-079E-4C94-8EC9-60363451EB40",
            #      "liveDefault": true,
            #      "liveMode": "WhenNeeded",
            #      "recordTo": "16ce3aa1-5f93-458a-abe5-5c95d9ed1372",
            #      "defaultPlayback": true,
            #      "useEdge": true
            #    }
            #  ],
            #}

            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRStream()
                oItem.DefaultPlayback = self.GetDictKeyValueBool(oDict, "defaultPlayback")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.LiveDefault = self.GetDictKeyValueBool(oDict, "liveDefault")
                oItem.LiveMode = self.GetDictKeyValueString(oDict, "liveMode")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")
                oItem.ParentId = parentId
                oItem.ParentType = parentType
                oItem.RecordToId = self.GetDictKeyValueString(oDict, "recordTo")
                oItem.StreamReferenceId = self.GetDictKeyValueString(oDict, "streamReferenceId")
                oItem.UseEdge = self.GetDictKeyValueBool(oDict, "useEdge")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def _Parse_UserDefinedEvent(self, oDict:dict, serviceMethodName:str) -> XPRUserDefinedEvent:
        """
        Parses a User Defined Event information JSON response, returning a managed class instance 
        that represents the response.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            An XPRUserDefinedEvent class instance that represents the JSON response.

        Raises:
            Exception:
                The method fails for any reason.  
        """
        methodKeyName:str = "UserDefinedEvent"
        oItem:XPRUserDefinedEvent = None

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            # {
            #   "displayName": "RequestPlayAudio",
            #   "id": "7605f8b0-7f5f-4432-b223-0bb2dc3f1f5c",
            #   "name": "RequestPlayAudio",
            #   "lastModified": "2023-06-25T21:22:20.3970000Z",
            #   "createdDate": "0001-01-01T00:00:00.0000000",
            #   "subtype": "System",
            #   "relations": {
            #     "self": {
            #       "type": "userDefinedEvents",
            #       "id": "7605f8b0-7f5f-4432-b223-0bb2dc3f1f5c"
            #     }
            #   }
            # }
        
            # were any results returned?
            if (oDict != None):

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_PROCESSING_DICTIONARY.format(methodKeyName), oDict)

                # parse base properties.
                oItem = XPRUserDefinedEvent()
                oItem.DateCreated = self.GetDictKeyValueDateTime(oDict, "createdDate")
                oItem.DateModified = self.GetDictKeyValueDateTime(oDict, "lastModified")
                oItem.DisplayName = self.GetDictKeyValueString(oDict, "displayName")
                oItem.Id = self.GetDictKeyValueString(oDict, "id")
                oItem.Name = self.GetDictKeyValueString(oDict, "name")
                oItem.SubType = self.GetDictKeyValueString(oDict, "subtype")

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_RESULT_OBJECT.format(methodKeyName, str(oItem)), oItem, excludeNonPublic=True)

            # return object to caller.
            return oItem

        except Exception as ex:

            # format unhandled exception.
            raise Exception(XPRAppMessages.EXCEPTION_PARSE_REST_RESULTS.format(methodKeyName, str(ex)))

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetAnalyticsEvents(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Analytics Event items.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRAnalyticsEvent items that contain AnalyticsEvent 
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetAnalyticsEvents.py
        ```
        </details>
        """
        serviceMethodName:str = "GetAnalyticsEvents"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving AnalyticsEvent information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/analyticsEvents?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/analyticsEvents{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRAnalyticsEvent))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_AnalyticsEvent(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetCameraGroups(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None, parentId:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more CameraGroups.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
            parentId (str):
                Parent Group identifier to retrieve child group items of, or null to retrieve top level groups.
                Default is None.

        Returns:
            An XPRCollection class of XPRCameraGroup items that contain camera group 
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetCameraGroups.py
        ```
        </details>
        """
        serviceMethodName:str = "GetCameraGroups"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Camera Group information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix if parent id specified.
                requrlParent:str = ""
                if (parentId):
                    requrlParent = "/{0}/cameraGroups".format(parentId)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/cameraGroups?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/cameraGroups{1}{2}".format(self.ApiGatewayUrlPrefix, requrlParent, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRDeviceGroup))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_DeviceGroup(itemNode, serviceMethodName, "CameraGroup"))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)


        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetCameraMotionDetections(self, cameraId:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Camera device MotionDetections.

        Args:
            cameraId (str):
                Globally unique identifier of the camera whose MotionDetections are to be retrieved.

        Returns:
            An XPRCollection class of XPRMotionDetection items that contain camera motion
            detection configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetCameraMotionDetections.py
        ```
        </details>
        """
        serviceMethodName:str = "GetCameraMotionDetections"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Camera Device MotionDetection information")

                # validations.
                if (cameraId == None) or (len(cameraId) == 0):
                    raise Exception(XPRAppMessages.ARGUMENT_REQUIRED_ERROR.format("cameraId"))

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/cameras/f0f31f69-36a2-46a3-80b6-48e4bf617db8/motionDetections

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/cameras/{1}/motionDetections".format(self.ApiGatewayUrlPrefix, cameraId)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRMotionDetection))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_MotionDetection(itemNode, serviceMethodName, "cameras"))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetCameras(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Camera devices.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRCamera items that contain camera 
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetCameras.py
        ```
        </details>
        """
        serviceMethodName:str = "GetCameras"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Camera Device information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/cameras?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/cameras{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRCamera))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_Camera(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetCameraStreams(self, cameraId:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Camera device streams.

        Args:
            cameraId (str):
                Globally unique identifier of the camera whose streams are to be retrieved.

        Returns:
            An XPRCollection class of XPRStream items that contain camera stream
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetCameraStreams.py
        ```
        </details>
        """
        serviceMethodName:str = "GetCameraStreams"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Camera Device Stream information")

                # validations.
                if (cameraId == None) or (len(cameraId) == 0):
                    raise Exception(XPRAppMessages.ARGUMENT_REQUIRED_ERROR.format("cameraId"))

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/cameras/f0f31f69-36a2-46a3-80b6-48e4bf617db8/streams

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/cameras/{1}/streams".format(self.ApiGatewayUrlPrefix, cameraId)

                reqheaders:list[str] = {
                    # TEST TODO:
                    #"Authorization": "Bearer {0}".format("eyJhbGciOiJSUzI1NiIsImtpZCI6IjI1N0ExNjRDQTVCQzA4MjU2RjQ4OTBBRDZEMDJGMDNFIiwidHlwIjoiSldUIn0.eyJpc3MiOiJodHRwOi8vd2luMTB2bS9JRFAiLCJuYmYiOjE2OTMyNDU3ODMsImlhdCI6MTY5MzI0NTc4MywiZXhwIjoxNjkzMjQ5MzgzLCJhdWQiOlsibWFuYWdlbWVudHNlcnZlciIsImh0dHA6Ly93aW4xMHZtL0lEUC9yZXNvdXJjZXMiXSwic2NvcGUiOlsibWFuYWdlbWVudHNlcnZlciJdLCJhbXIiOlsicHdkIl0sImNsaWVudF9pZCI6IkdyYW50VmFsaWRhdG9yQ2xpZW50Iiwic3ViIjoiOTlFNTE1NUItNUZCNi00QzdCLTkxQTgtNzA1OTlGMTEyNDA2IiwiYXV0aF90aW1lIjoxNjkzMjQ1NzgzLCJpZHAiOiJsb2NhbCIsIm5hbWUiOiJ4cGFkbWluIiwidXBkYXRlZF9hdCI6IjE2OTMyNDQ5MzQiLCJqdGkiOiJGRUYwMTk4QTE4OURGRTIxQTg5NEE4RTA1QkVCQkM3MiJ9.rVZM8VBUHBIrliJnt2JMfFwmV2trEJx2gd2wJgYJiP3ul1gM6tFpf0acnZU4QTW9dOqWQ_jUyyXCgBGyBf7etPeFualfJwOhM3_a9Cec5BhWycZtpzpcZpTIPM8EEAbd2UrL3DwacvPSx1L4mtSDI-n1kXh4vsPHSsdWG-gAqkjBV9al7z63m5M08dOlBCjbPOpCQdzSgXDgjODeEOCQRJ1h7JVa0zm7VJDA1O86-KYvfTtLnFFDCvqJHA2h5tGzMj_7Zb8628If4xO8LZyx1Bn9gJzKGjKbTFTZmFB0-NFEL13shlMc6RhpvcuY1xulgcn2991SvaXMh1x_JuoV-Q"),
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRStream))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:

                    # get stream parent id and type.
                    parentType:str = "cameras"
                    parentId:str = self.GetRelationParentTypeId(itemNode, "parent", parentType, serviceMethodName)
 
                    # process stream details.
                    collKeyName:str = "stream"
                    collStreamNodes:dict = self.GetDictItems(itemNode, collKeyName)
                    for streamNode in collStreamNodes:
                        oResult.append(self._Parse_Stream(streamNode, serviceMethodName, parentId, parentType))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetChildSites(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None, parentId:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Child Sites.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
            parentId (str):
                Parent Site identifier to retrieve child site items of, or null to retrieve top level sites.
                Default is None.

        Returns:
            An XPRCollection class of XPRChildSite items that contain site
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetChildSites.py
        ```
        </details>
        """
        serviceMethodName:str = "GetChildSites"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving ChildSite information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix if parent id specified.
                requrlParent:str = ""
                if (parentId):
                    requrlParent = "/{0}/childSites".format(parentId)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/childSites?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/childSites{1}{2}".format(self.ApiGatewayUrlPrefix, requrlParent, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRChildSite))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_ChildSite(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetEventTypeGroups(self) -> XPRCollection:
        """
        Returns configuration information for one or more EventTypeGroups.

        Returns:
            An XPRCollection class of XPREventTypeGroup items that contain EventType group 
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetEventTypeGroups.py
        ```
        </details>
        """
        serviceMethodName:str = "GetEventTypeGroups"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving EventType Group information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/EventTypeGroups?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/EventTypeGroups".format(self.ApiGatewayUrlPrefix)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPREventTypeGroup))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_EventTypeGroup(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)


        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetEventTypes(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more EventType items.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPREventType items that contain EventType 
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetEventTypes.py
        ```
        </details>
        """
        serviceMethodName:str = "GetEventTypes"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving EventType information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/eventTypes?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/eventTypes{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPREventType))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_EventType(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)

            
    def GetGenericEventDataSources(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Generic Event DataSource items.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRGenericEventDataSource items that contain GenericEventDataSource 
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetGenericEventDataSources.py
        ```
        </details>
        """
        serviceMethodName:str = "GetGenericEventDataSources"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving GenericEventDataSource information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/genericEventDataSources?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/genericEventDataSources{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRGenericEventDataSource))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_GenericEventDataSource(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetGenericEvents(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Generic Event items.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRGenericEvent items that contain GenericEvent 
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetGenericEvents.py
        ```
        </details>
        """
        serviceMethodName:str = "GetGenericEvents"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving GenericEvent information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/genericEvents?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/genericEvents{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRGenericEvent))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_GenericEvent(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetHardware(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Hardware devices.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRHardware items that contain hardware
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetHardware.py
        ```
        </details>
        """
        serviceMethodName:str = "GetHardware"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Hardware Device information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/Hardware?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/Hardware{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRHardware))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_Hardware(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetInputEventGroups(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None, parentId:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more InputEventGroups.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
            parentId (str):
                Parent Group identifier to retrieve child group items of, or null to retrieve top level groups.
                Default is None.

        Returns:
            An XPRCollection class of XPRDeviceGroup items that contain device group
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetInputEventGroups.py
        ```
        </details>
        """
        serviceMethodName:str = "GetInputEventGroups"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving InputEvent Group information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix if parent id specified.
                requrlParent:str = ""
                if (parentId):
                    requrlParent = "/{0}/inputEventGroups".format(parentId)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/inputEventGroups?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/inputEventGroups{1}{2}".format(self.ApiGatewayUrlPrefix, requrlParent, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRDeviceGroup))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_DeviceGroup(itemNode, serviceMethodName, "InputEventGroup"))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetInputEvents(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more InputEvent devices.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRInputEvent items that contain input event
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetInputEvents.py
        ```
        </details>
        """
        serviceMethodName:str = "GetInputEvents"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving InputEvent Device information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/inputEvents?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/inputEvents{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRInputEvent))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_InputEvent(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetLicenseDetails(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns an Detail of all product license information.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRLicenseDetail items that contain license detail
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetLicenseDetails.py
        ```
        </details>
        """
        serviceMethodName:str = "GetLicenseDetails"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving License Detail information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/licenseDetails?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/licenseDetails{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRLicenseDetail))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_LicenseDetail(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetLicenseInformations(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more LicenseInformations.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRLicenseInformation items that contain license
            information configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetLicenseInformations.py
        ```
        </details>
        """
        serviceMethodName:str = "GetLicenseInformations"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving License information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/licenseInformations?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/licenseInformations{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRLicenseInformation))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_LicenseInformation(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetLicenseOverviews(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns an overview of all product license information.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRLicenseOverview items that contain license
            overview configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetLicenseOverviews.py
        ```
        </details>
        """
        serviceMethodName:str = "GetLicenseOverviews"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving License Overview information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/licenseOverviewAll?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/licenseOverviewAll{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRLicenseOverview))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_LicenseOverview(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetLicenseInstalledProducts(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns detailed information of all installed product licenses.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRLicenseProduct items that contain license
            product configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetLicenseInstalledProducts.py
        ```
        </details>
        """
        serviceMethodName:str = "GetLicenseProducts"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving License Product information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/licenseInstalledProducts?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/licenseInstalledProducts{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRLicenseProduct))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_LicenseProduct(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetMetadataGroups(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None, parentId:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more MetadataGroups.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
            parentId (str):
                Parent Group identifier to retrieve child group items of, or null to retrieve top level groups.
                Default is None.

        Returns:
            An XPRCollection class of XPRDeviceGroup items that contain device group
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetMetadataGroups.py
        ```
        </details>
        """
        serviceMethodName:str = "GetMetadataGroups"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Metadata Group information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix if parent id specified.
                requrlParent:str = ""
                if (parentId):
                    requrlParent = "/{0}/metadataGroups".format(parentId)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/metadataGroups?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/metadataGroups{1}{2}".format(self.ApiGatewayUrlPrefix, requrlParent, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRDeviceGroup))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_DeviceGroup(itemNode, serviceMethodName, "MetadataGroup"))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetMetadatas(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Metadata devices.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRMetadata items that contain metadata
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetMetadatas.py
        ```
        </details>
        """
        serviceMethodName:str = "GetMetadatas"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Metadata Device information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/metadata?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/metadata{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRMetadata))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_Metadata(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetMicrophoneGroups(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None, parentId:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more MicrophoneGroups.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
            parentId (str):
                Parent Group identifier to retrieve child group items of, or null to retrieve top level groups.
                Default is None.

        Returns:
            An XPRCollection class of XPRDeviceGroup items that contain device group
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetMicrophoneGroups.py
        ```
        </details>
        """
        serviceMethodName:str = "GetMicrophoneGroups"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Microphone Group information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix if parent id specified.
                requrlParent:str = ""
                if (parentId):
                    requrlParent = "/{0}/MicrophoneGroups".format(parentId)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/MicrophoneGroups?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/MicrophoneGroups{1}{2}".format(self.ApiGatewayUrlPrefix, requrlParent, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRDeviceGroup))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_DeviceGroup(itemNode, serviceMethodName, "MicrophoneGroup"))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetMicrophones(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Microphone devices.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRMicrophone items that contain microphone
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetMicrophones.py
        ```
        </details>
        """
        serviceMethodName:str = "GetMicrophones"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Microphone Device information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/microphones?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/microphones{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRMicrophone))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_Microphone(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetOutputGroups(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None, parentId:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more OutputGroups.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
            parentId (str):
                Parent Group identifier to retrieve child group items of, or null to retrieve top level groups.
                Default is None.

        Returns:
            An XPRCollection class of XPRDeviceGroup items that contain device group
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetOutputGroups.py
        ```
        </details>
        """
        serviceMethodName:str = "GetOutputGroups"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Output Group information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix if parent id specified.
                requrlParent:str = ""
                if (parentId):
                    requrlParent = "/{0}/OutputGroups".format(parentId)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/OutputGroups?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/OutputGroups{1}{2}".format(self.ApiGatewayUrlPrefix, requrlParent, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRDeviceGroup))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_DeviceGroup(itemNode, serviceMethodName, "OutputGroup"))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetOutputs(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Output devices.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPROutput items that contain output
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetOutputs.py
        ```
        </details>
        """
        serviceMethodName:str = "GetOutputs"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Output Device information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/outputs?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/outputs{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPROutput))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_Output(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetParentTypeId(self, oDict:dict, parentTypeName:str, typeName:str, serviceMethodName:str) -> str:
        """
        Parses a JSON response dictionary for the parent key name, type name, and id value.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            parentTypeName (str):
                The parent key name that contains a type and id sub-key (e.g. "recordingStorage", etc).
            typeName (str):
                The type name that contains an id value (e.g. "storages", etc).
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            The parent type id value if present; otherwise, None.

        This can be used for any methods that return a type id within a "parent" response.
        """
        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #"recordingStorage": {
            #  "type": "storages",
            #  "id": "42dd23f1-7513-48a0-bdc3-1e26351d7cd8"

            # were any results returned?
            if (oDict != None):

                # is a parent key present?  if not, then we are done.
                if (not self.DictHasKey(oDict, parentTypeName)):
                    return None

                # reference the parent key.
                oDictParent:dict = oDict[parentTypeName]

                # is a parent.type key present?  if not, then we are done.
                if (not self.DictHasKey(oDictParent, "type")):
                    return None

                # if parent.type key is not the specified type name, then we are done.
                if (not oDictParent["type"] == typeName):
                    return None

                # is a parent.id key present?  if so, then return the value.
                if (self.DictHasKey(oDictParent, "id")):
                    return oDictParent["id"]

                return None

        except Exception as ex:

            # ignonre exceptions
            _logsi.LogException("Could not retrieve relational Hardware Id from {0} Request response.".format(serviceMethodName), ex)
            raise 

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetRecordingServers(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Recording Servers.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRRecordingServer items that contain recording
            server configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetRecordingServers.py
        ```
        </details>
        """
        serviceMethodName:str = "GetRecordingServers"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving RecordingServer information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/recordingServers?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/recordingServers{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRRecordingServer))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_RecordingServer(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetRelationParentTypeId(self, oDict:dict, relationKeyName:str, typeName:str, serviceMethodName:str) -> str:
        """
        Parses a JSON response dictionary for the related key name, type name, and id value.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            relationKeyName (str):
                The relation key name that contains a type and id sub-key (e.g. "parent", "self", etc).
            typeName (str):
                The type name that contains an id value (e.g. "hardware", "cameras", etc).
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            The related type id value if present; otherwise, None.

        This can be used for any methods that return a type id within a "relations" response.

        For example:
            "relations": {
              "parent": {
                  "type": "hardware",
                  "id": "08cf6a24-c7ab-4b50-80e0-5a56cf624c5f"
              },
            }
        """
        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug)

            # JSON response example:
            #  "relations": {
            #    "parent": {
            #      "type": "hardware",
            #      "id": "08cf6a24-c7ab-4b50-80e0-5a56cf624c5f"
            #    },
            #  }

            # were any results returned?
            if (oDict != None):

                # is a relations key present?  if not, then we are done.
                if (not self.DictHasKey(oDict, "relations")):
                    return None

                # reference the relations key.
                oDictRelations:dict = oDict["relations"]

                # is a relations.[keyname] key present?  if not, then we are done.
                if (not self.DictHasKey(oDictRelations, relationKeyName)):
                    return None

                # reference the relations.[keyname] subkey.
                oDictParent:dict = oDictRelations[relationKeyName]

                # is a relations.[keyname].type key present?  if not, then we are done.
                if (not self.DictHasKey(oDictParent, "type")):
                    return None

                # if relations.[keyname].type key is not the specified type name, then we are done.
                if (not oDictParent["type"] == typeName):
                    return None

                # is a relations.parent.id key present?  if so, then return the value.
                if (self.DictHasKey(oDictParent, "id")):
                    return oDictParent["id"]

                return None

        except Exception as ex:

            # ignonre exceptions
            _logsi.LogException("Could not retrieve relational Hardware Id from {0} Request response.".format(serviceMethodName), ex)
            raise 

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetRelationParentTypeIdHardware(self, oDict:dict, serviceMethodName:str) -> str:
        """
        Parses a JSON response dictionary for the related parent hardware type id value.

        Args:
            oDict (dict):
                A dictionary object that represents the JSON response.
            serviceMethodName (str):
                Name of the service method that was called.  
                Example: "GetCameras", etc.

        Returns:
            The related parent hardware type id value if present; otherwise, None.

        This can be used for any methods that return a hardware id within a "relations" response.
        """
        return self.GetRelationParentTypeId(oDict, "parent", "hardware", serviceMethodName)


    def GetSiteOwner(self, siteId:str=None) -> XPRSiteOwner:
        """
        Returns site owner information for the specified site id.

        Args:
            siteId (str):
                Site identifier to retrieve ownership information for.  This can be a main site id, or
                a child site id.  
                Default is None, which will retrieve ownership information for the main site.

        Returns:
            An XPRSiteOwner class that contains Site ownership details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetSiteOwner.py
        ```
        </details>
        """
        serviceMethodName:str = "GetSiteOwner"
        oResult:XPRSiteOwner = XPRSiteOwner()

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Site ownership information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/owner?disabled    or ...
                # GET http://myapigateway.example.com:80/api/rest/v1/sites/fc9e48ce-a39b-4327-8b92-32b012688944/owner?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                if (siteId == None) or (len(siteId) == 0):
                    requrl:str = "{0}/api/rest/v1/owner?disabled".format(self.ApiGatewayUrlPrefix)
                else:
                    requrl:str = "{0}/api/rest/v1/sites/{1}/owner?disabled".format(self.ApiGatewayUrlPrefix, siteId)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRSiteOwner))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult = self._Parse_SiteOwner(itemNode, serviceMethodName)
                    break   # only process the first entry.

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetSites(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Sites.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRSite items that contain site
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetSites.py
        ```
        </details>
        """
        serviceMethodName:str = "GetSites"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Site information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/sites?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/sites{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRSite))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_Site(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetSpeakerGroups(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None, parentId:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more SpeakerGroups.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
            parentId (str):
                Parent Group identifier to retrieve child group items of, or null to retrieve top level groups.
                Default is None.

        Returns:
            An XPRCollection class of XPRDeviceGroup items that contain device group
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetSpeakerGroups.py
        ```
        </details>
        """
        serviceMethodName:str = "GetSpeakerGroups"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Speaker Group information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix if parent id specified.
                requrlParent:str = ""
                if (parentId):
                    requrlParent = "/{0}/SpeakerGroups".format(parentId)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/SpeakerGroups?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/SpeakerGroups{1}{2}".format(self.ApiGatewayUrlPrefix, requrlParent, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRDeviceGroup))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_DeviceGroup(itemNode, serviceMethodName, "SpeakerGroup"))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetSpeakers(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more Speaker devices.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRSpeaker items that contain speaker
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetSpeakers.py
        ```
        </details>
        """
        serviceMethodName:str = "GetSpeakers"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving Speaker Device information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/speakers?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/speakers{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRSpeaker))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_Speaker(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetStateGroups(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more StateGroup items.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRStateGroup items that contain StateGroup 
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetStateGroups.py
        ```
        </details>
        """
        serviceMethodName:str = "GetStateGroups"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving StateGroup information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/stateGroups?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/stateGroups{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRStateGroup))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_StateGroup(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)


    def GetUserDefinedEvents(self, includeDisabled:bool=True, filterName:str=None, filterOperator:XPRFilterOperator=None, filterValue:str=None) -> XPRCollection:
        """
        Returns configuration information for one or more UserDefinedEvent items.

        Args:
            includeDisabled (bool):
                True to include disabled items in the returned information;  
                otherwise False to return only enabled items.  
                Default is True.
            filterName (str):
                Used to filter data returned using a property name (e.g. "name", "description", etc).  
                The value will be url-encoded, as it is used as part of a querystring.
                Default value is None.
            filterOperator (str):
                Type of filtering to perform (e.g. contains, equals, lt, etc).  
            filterValue (str):
                Value to search for if filtering returned data (e.g. "MyName", "MyDescription", etc).  
                The value will be url-encoded, as it is used as part of a querystring.

        Returns:
            An XPRCollection class of XPRUserDefinedEvent items that contain UserDefinedEvent 
            configuration details.

        Raises:
            XPRRestServiceException:
                The XProtect REST Server returned a failed response.
            XPRException:
                The method fails for any other reason.  

        If any of the filter arguments (filterName, filterOperator, filterValue) are specified, then ALL 
        of the filter arguments are required.  A filter will not be applied if ANY of the filter arguments 
        are missing.

        <details>
          <summary>Sample Code</summary><br/>
        ```python
        .. include:: ../docs/include/samplecode/XPRRestService/GetUserDefinedEvents.py
        ```
        </details>
        """
        serviceMethodName:str = "GetUserDefinedEvents"

        try:

            # trace.
            _logsi.EnterMethod(SILevel.Debug) 

            with self._fLock:

                # trace.
                _logsi.LogMessage("Retrieving UserDefinedEvent information")

                # automatic token renewal check and logininfo validation.
                self._AutoTokenRenewalCheck(serviceMethodName)

                # formulate request url suffix with search parameters and options.
                requrlFilter:str = self._GetFilterQueryString(includeDisabled, filterName, filterOperator, filterValue)

                # REST request example(url, headers):

                # GET http://myapigateway.example.com:80/api/rest/v1/userDefinedEvents?disabled

                #Accept-Encoding: gzip, deflate, br
                #Connection: keep-alive
                #Content-Type: application/json; charset=utf-8
 
                # formulate xprotect rest service request parameters (url, headers, body).
                requrl:str = "{0}/api/rest/v1/userDefinedEvents{1}".format(self.ApiGatewayUrlPrefix, requrlFilter)

                reqheaders:list[str] = {
                    "Authorization": "Bearer {0}".format(self._fLoginInfo.Token),
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    }

                reqbody:str = ""

                # create request object.
                req:Request = Request('GET', requrl, headers=reqheaders, data=reqbody)

                # prepare the request.
                reqSess = Session()
                reqprep = reqSess.prepare_request(req)

                # trace.
                if (_logsi.IsOn(SILevel.Verbose)):
                    _logsi.LogObject(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST.format(serviceMethodName), reqprep)
                    _logsi.LogSource(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_BODY.format(serviceMethodName), reqbody, SISourceId.Xml)
                    _logsi.LogDictionary(SILevel.Verbose, MSG_TRACE_METHOD_RESTREQUEST_HEADERS.format(serviceMethodName), reqprep.headers)

                # send the request.
                resp = reqSess.send(reqprep, verify=self.IsSslVerifyEnabled)

                # check response code, and raise an exception if it failed.
                oDict:dict = self.CheckRestResponseCode(serviceMethodName, req, resp)

                # initialize returned results collection.
                oResult:XPRCollection = XPRCollection((XPRUserDefinedEvent))

                # process rest service response dictionary item node(s).
                collKeyName:str = "array"
                collNodes:dict = self.GetDictItems(oDict, collKeyName)
                for itemNode in collNodes:
                    oResult.append(self._Parse_UserDefinedEvent(itemNode, serviceMethodName))

                # trace.
                _logsi.LogCollection(SILevel.Verbose, MSG_TRACE_RESULT_COLLECTION.format(serviceMethodName), oResult)

                # return result to caller.
                return oResult

        except XPRException: raise  # pass thru exceptions already handled
        except Exception as ex:

            # format unhandled exception.
            raise XPRException(XPRAppMessages.UNHANDLED_EXCEPTION.format(serviceMethodName, str(ex)), ex, _logsi)

        finally:

            # trace.
            _logsi.LeaveMethod(SILevel.Debug)
