"""
Module: xputils.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/07/07 | 1.0.0.0     | Initial Version.  

</details>
"""

# external package imports.
from datetime import datetime
import sys

"""
Utility module of helper functions.
"""

def static_init(cls):
    """
    Define the decorator used to call an initializer for a class with all static methods.
    This allows static variables to be initialized one time for the class.
    """
    if getattr(cls, "static_init", None):
        cls.static_init()
    return cls


def export(fn):
    """
    Define the decorator used to modify a module's "__all__" variable.
    This avoids us having to manually modify a module's "__all__" variable when adding new classes.
    """
    mod = sys.modules[fn.__module__]
    if hasattr(mod, '__all__'):
        mod.__all__.append(fn.__name__)
    else:
        mod.__all__ = [fn.__name__]

    return fn
    

class Event:
    """
    C# like event processing in Python3.

    <details>
        <summary>View Sample Code</summary>
    ```python
    # Define the class that will be raising events:
    class MyFileWatcher:
        def __init__(self):
            self.fileChanged = Event()      # define event

        def watchFiles(self):
            source_path = "foo"
            self.fileChanged(source_path)   # fire event

    def log_file_change(source_path):       # event handler 1
        print "%r changed." % (source_path,)

    def log_file_change2(source_path):      # event handler 2
        print "%r changed!" % (source_path,)

    # Define the code that will be handling raised events.
    watcher              = MyFileWatcher()
    watcher.fileChanged += log_file_change2
    watcher.fileChanged += log_file_change
    watcher.fileChanged -= log_file_change2
    watcher.watchFiles()
    ```
    </details>
    """

    def __init__(self, *args) -> None:
        """
        Initializes a new instance of the class.
        """
        self.handlers = set()

    def fire(self, *args, **kargs):
        """
        Calls (i.e. "fires") all method handlers defined for this event.
        """
        for handler in self.handlers:
            handler(*args, **kargs)

    def getHandlerCount(self):
        """
        Returns the number of method handlers defined for this event.
        """
        return len(self.handlers)

    def handle(self, handler):
        """
        Adds a method handler for this event.
        """
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        """
        Removes the specified method handler for this event.

        Args:
            handler (object):
                The method handler to remove.

        This method will not throw an exception.
        """
        try:
            self.handlers.remove(handler)
        except:
            #raise ValueError("Handler is not handling this event, so cannot unhandle it.")
            pass   # ignore exceptions.
        return self

    def unhandle_all(self):
        """
        Removes all method handlers (if any) for this event.

        This method will not throw an exception.
        """
        try:
            self.handlers.clear()
        except:
            #raise ValueError("Handler is not handling this event, so cannot unhandle all.")
            pass   # ignore exceptions.
        return self

    # alias method definitions.
    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount


class DataTypeHelper:
    """
    Helper class used for processing different types of data.
    """

    @staticmethod
    def BoolToStringYesNo(value:bool) -> str:
        """
        Converts a boolean value to a "Yes" (true) or "No" (false) string.

        Args:
            value (bool):
                Boolean value to convert.

        Returns:
            A "Yes" or "No" string value.
        """
        if (value):
            return "Yes"
        else:
            return "No"

    @staticmethod
    def BoolFromString(value:str) -> bool:
        """
        Converts a string to a boolean value.  

        Args:
            value (str):
                String value to convert.

        Returns:
            A bool value.

        True is returned if the value argument contains "yes", "true", "t", or "1";  
        otherwise, False is returned.
        """
        return value.lower() in ("yes", "true", "t", "1")


    @staticmethod
    def DateTimeFromString(value:str, argumentName:str, raiseExceptionIfNull:bool=True) -> datetime:
        """
        Converts a string to a datetime value.  

        Args:
            value (str):
                String value to convert.
            argumentName (str):
                Argument Name the datetime string was loaded from - used in exception
                details if the string could not be converted successfully.
            raiseExceptionIfNull (bool):
                If True, and Exception will be raised if the string could not be converted
                to a date or if the value is null; otherwise, False to not raise an exception.

        Returns:
            A datetime value.

        True is returned if the value argument contains "yes", "true", "t", or "1";  
        otherwise, False is returned.

        Supported examples for datetime string are:
        - "0001-01-01T00:00:00.0000000"  
        - "2023-07-24T17:12:31.0210000Z"  
        - "2023-07-24T17:12:31.0210Z"  
        - "2023-07-24T17:12:31Z"  
        """
        # parse response result.
        datetime_str = value
        result:datetime = None

        if (datetime_str != None):

            # if time returned is "0001-00-00 ..." then it denotes that the device
            # did not return any data (e.g. camera is off, disconnected, etc).  we
            # do not treat this as an error condition since the web-service does
            # not treat it as an error condition.
            if (datetime_str == "0001-01-01T00:00:00.0000000"):

                result = datetime.strptime(datetime_str[:-1], "%Y-%m-%dT%H:%M:%S.%f")

            else:

                try:

                    # get the datetime string length (do it once for performance):
                    datetime_len:int = len(datetime_str)

                    # figure out which format the datetime is based upon it's string representation:
                    if (datetime_len == 28):     # e.g. "2023-07-24T17:12:31.0210000Z"
                        result = datetime.strptime(datetime_str[:-4]+"Z", "%Y-%m-%dT%H:%M:%S.%f%z")
                    elif (datetime_len == 23):   # e.g. "2023-06-26T23:49:14.05Z"
                        result = datetime.strptime(datetime_str[:-1]+"Z", "%Y-%m-%dT%H:%M:%S.%f%z")
                    elif (datetime_len == 24):   # e.g. "2023-06-26T23:49:14.051Z"
                        result = datetime.strptime(datetime_str[:-2]+"Z", "%Y-%m-%dT%H:%M:%S.%f%z")
                    elif (datetime_len == 20):   # e.g. "2023-07-24T17:12:31Z"
                        result = datetime.strptime(datetime_str[:-4]+"Z", "%Y-%m-%dT%H:%M:%S%z")
                    elif (datetime_len == 19):   # e.g. "2023-07-24T17:12:31"
                        result = datetime.strptime(datetime_str+"Z", "%Y-%m-%dT%H:%M:%S%z")
                    elif (datetime_len == 33) and (datetime_str[datetime_len-3:datetime_len-2] == ":"):
                        # 7 digit MS to 6 digits # e.g. "2023-09-07T12:55:54.3970000-05:00"                        
                        # only use first 6 digits of milliseconds value, and then try to convert it.
                        tzOffset = datetime_str[datetime_len-6:datetime_len]
                        dtValue6MS =  datetime_str[0:datetime_len-7]
                        result = datetime.strptime(dtValue6MS + tzOffset, "%Y-%m-%dT%H:%M:%S.%f%z")
                    else:                           # e.g. "2023-07-24T17:12:31.0210Z"
                        result = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%f%Z")

                except ValueError as ex:
                    pass
        
        # was string converted to a datetime?
        if (result == None):
            if (raiseExceptionIfNull):
                raise Exception("The <{0}> value contains a datetime format string that is unknown or null.".format(argumentName))

        # return to caller.
        return result
