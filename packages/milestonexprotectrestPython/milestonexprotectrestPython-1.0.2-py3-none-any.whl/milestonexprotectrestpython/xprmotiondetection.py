"""
Module: xprmotiondetection.py

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
class XPRMotionDetection:
    """
    Motion Detection information.
    
    Threadsafety:
        This class is fully thread-safe.

    More information about Motion Detection configuration can be found on the
    <a target="_blank" href="https://doc.milestonesys.com/2023R2/en-US/standard_features/sf_mc/sf_ui/mc_devicestabs_devices.htm#MC_MotionTabDevices.htm">vendor documentation page</a>.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fDetectionMethod:str = None
        self._fDisplayName:str = None
        self._fEnabled:bool = None
        self._fExcludeRegions:str = None
        self._fGenerateMotionMetadata:bool = False
        self._fGridSize:str = None
        self._fHardwareAccelerationMode:str = None
        self._fId:str = None
        self._fKeyframesOnly:bool = None
        self._fManualSensitivity:int = 0
        self._fManualSensitivityEnabled:bool = None
        self._fParentId:str = None
        self._fParentType:str = None
        self._fProcessTime:str = None
        self._fThreshold:int = 0
        self._fUseExcludeRegions:bool = False


    @property
    def DetectionMethod(self) -> str:
        """ 
        Motion detection method used to optimize motion detection by analyzing only 
        a percentage of the image. Valid values are:  
        - Normal  
        - Optimized  
        - Fast  

        Returns:
            The DetectionMethod property value.
        """
        return self._fDetectionMethod

    @DetectionMethod.setter
    def DetectionMethod(self, value:str) -> None:
        """ 
        Sets the DetectionMethod property value.
        """
        self._fDetectionMethod = value


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
        True if motion detection is enabled; otherwise, False.

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
    def ExcludeRegions(self) -> str:
        """ 
        Defines regions of the camera view to exclude from motion detection.

        Returns:
            The ExcludeRegions property value.

        Excluding motion detection from specific areas helps you avoid detection of irrelevant motion, 
        for example if the camera covers an area where a tree is swaying in the wind or where cars 
        regularly pass by in the background.
        """
        return self._fExcludeRegions

    @ExcludeRegions.setter
    def ExcludeRegions(self, value:str) -> None:
        """ 
        Sets the ExcludeRegions property value.
        """
        self._fExcludeRegions = value


    @property
    def GenerateMotionMetadata(self) -> bool:
        """ 
        True to generate motion metadata for smart search function; otherwise, False.

        Returns:
            The GenerateMotionMetadata property value.
        """
        return self._fGenerateMotionMetadata

    @GenerateMotionMetadata.setter
    def GenerateMotionMetadata(self, value:bool) -> None:
        """ 
        Sets the GenerateMotionMetadata property value.
        """
        self._fGenerateMotionMetadata = value


    @property
    def GridSize(self) -> str:
        """ 
        Grid size used when defining exclude regions.  Valid values are:
        - 8x8  
        - 16x16  
        - 32x32  
        - 64x64  

        Returns:
            The GridSize property value.
        """
        return self._fGridSize

    @GridSize.setter
    def GridSize(self, value:str) -> None:
        """ 
        Sets the GridSize property value.
        """
        self._fGridSize = value


    @property
    def HardwareAccelerationMode(self) -> str:
        """ 
        Hardware acceleration mode that is in use.  Valid values are:
        - Automatic = hardware acceleration enabled.  
        - Off = hardware acceleration disabled.  

        Returns:
            The HardwareAccelerationMode property value.
        """
        return self._fHardwareAccelerationMode

    @HardwareAccelerationMode.setter
    def HardwareAccelerationMode(self, value:str) -> None:
        """ 
        Sets the HardwareAccelerationMode property value.
        """
        self._fHardwareAccelerationMode = value


    @property
    def Id(self) -> str:
        """ 
        Globally unique identifier of the motion detection item.

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
    def KeyframesOnly(self) -> bool:
        """ 
        True to do motion detection on keyframes only; otherwise, False to do motion
        detection on the entire video stream.  

        Returns:
            The KeyframesOnly property value.

        Only applies to MPEG-4/H.264/H.265.

        Motion detection on keyframes reduces the amount of processing power used to carry 
        out the analysis.
        """
        return self._fKeyframesOnly

    @KeyframesOnly.setter
    def KeyframesOnly(self, value:bool) -> None:
        """ 
        Sets the KeyframesOnly property value.
        """
        self._fKeyframesOnly = value


    @property
    def ManualSensitivity(self) -> int:
        """ 
        Determines how much each pixel in the image must change before it is 
        regarded as motion.  Value in range 0 - 765.

        Returns:
            The ManualSensitivity property value.
        """
        return self._fManualSensitivity

    @ManualSensitivity.setter
    def ManualSensitivity(self, value:int) -> None:
        """ 
        Sets the ManualSensitivity property value.
        """
        self._fManualSensitivity = value


    @property
    def ManualSensitivityEnabled(self) -> bool:
        """ 
        True to enable manual sensitivity settings; otherwise, False to
        utilize automatic sensitivity settings.

        Returns:
            The ManualSensitivityEnabled property value.
        """
        return self._fManualSensitivityEnabled

    @ManualSensitivityEnabled.setter
    def ManualSensitivityEnabled(self, value:bool) -> None:
        """ 
        Sets the ManualSensitivityEnabled property value.
        """
        self._fManualSensitivityEnabled = value


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
    def ProcessTime(self) -> str:
        """ 
        Image processing interval that determines how often the system performs 
        the motion detection analysis.  
        Default value is every 500 milliseconds.

        Motion detection check interval that specifies how often to check for motion. 
        Valid values are:
        - Ms100 = every 100 milliseconds.
        - Ms250 = every 250 milliseconds.
        - Ms500 = every 500 milliseconds.
        - Ms750 = every 750 milliseconds.
        - Ms1000 = every 1000 milliseconds (or 1 second).

        Returns:
            The ProcessTime property value.

        The interval is applied if the actual frame rate is higher than the interval you set here.
        For example, every 1000 milliseconds are once every second.
        """
        return self._fProcessTime

    @ProcessTime.setter
    def ProcessTime(self, value:str) -> None:
        """ 
        Sets the ProcessTime property value.
        """
        self._fProcessTime = value


    @property
    def Threshold(self) -> int:
        """ 
        Determine how many pixels in the image must change before it is regarded 
        as motion and triggers a motion event.  Value in range 0 - 10000.

        Returns:
            The Threshold property value.
        """
        return self._fThreshold

    @Threshold.setter
    def Threshold(self, value:int) -> None:
        """ 
        Sets the Threshold property value.
        """
        self._fThreshold = value


    @property
    def UseExcludeRegions(self) -> bool:
        """ 
        True to enable exclude regions in the motion detection; otherwise, False to
        include all pixels in the view for motion detection.

        Returns:
            The UseExcludeRegions property value.
        """
        return self._fUseExcludeRegions

    @UseExcludeRegions.setter
    def UseExcludeRegions(self, value:bool) -> None:
        """ 
        Sets the UseExcludeRegions property value.
        """
        self._fUseExcludeRegions = value


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
            if (isinstance(self, XPRMotionDetection)) and (isinstance(other, XPRMotionDetection)):
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
            if (isinstance(self, XPRMotionDetection)) and (isinstance(other, XPRMotionDetection)):
                return self.DisplayName < other.DisplayName
            return False
