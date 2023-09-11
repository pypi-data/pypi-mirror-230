"""
Module: xprconst.py

<details>
  <summary>Revision History</summary>

| Date       | Version     | Description
| ---------- | ----------- | ----------------------
| 2023/07/11 | 1.0.0.0     | Initial Version.  

</details>
"""

# our package imports.
# none.

# constants are placed in this file if they are used across multiple files.
# the only exception to this is for the VERSION constant, which is placed here for convenience.

VERSION:str = "1.0.1"
""" 
Current version of the Milestone XProtect REST Python3 Library. 
"""

PACKAGENAME:str = "milestonexprotectrestpython"
"""
Name of our package (used by PDoc Documentation build).
"""

# properties used in PDOC documentation build.

PDOC_BRAND_ICON_URL:str = "https://www.milestonesys.com/video-technology/platform/xprotect/"
"""
PDoc Documentation brand icon link url that is displayed in the help document TOC.
Value = "https://www.milestonesys.com/video-technology/platform/xprotect/"
"""

PDOC_BRAND_ICON_URL_SRC:str = "milestonexprotect.ico"
"""
PDoc Documentation brand icon link url that is displayed in the help document TOC.
Value = "milestonexprotect.ico"
"""

PDOC_BRAND_ICON_URL_TITLE:str = "A XProtect Client"
"""
PDoc Documentation brand icon link title that is displayed in the help document TOC.
Value = "A XProtect Client"
"""

# Miscellaneous constants:

UNKNOWN_VALUE:str = "<unknown>"
"""
Indicates if an event argument value is unknown for event argument objects that are displayed as a string.

Value: 
    `"<unknown>"`
"""


# Application trace messages.
MSG_TRACE_METHOD_RESTREQUEST:str = "{0} REST request"
"""
{0} REST request
"""

MSG_TRACE_METHOD_RESTREQUEST_HEADERS:str = "{0} REST request headers"
"""
{0} REST request headers
"""

MSG_TRACE_METHOD_RESTREQUEST_BODY:str = "{0} REST request body"
"""
{0} REST request body 
"""

MSG_TRACE_METHOD_RESTRESPONSE:str = "{0} REST response"
"""
{0} REST response
"""

MSG_TRACE_METHOD_RESTRESPONSE_BODY:str = "{0} REST response body"
"""
{0} REST response body
"""

MSG_TRACE_PROCESSING_DICTIONARY:str = "Processing dictionary \"{0}\" node"
"""
Processing dictionary \"{0}\" node"
"""

MSG_TRACE_PROCESSING_DICTIONARY_COLLECTION:str = "Processing dictionary collection \"{0}\" node, and any \"{1}\" item nodes"
"""
Processing dictionary \"{0}\" collection node, and any \"{1}\" item nodes
"""

MSG_TRACE_RESULT_COLLECTION:str = "{0} Collection results"
"""
{0} Collection results
"""

MSG_TRACE_RESULT_OBJECT:str = "{0} object created: {1}"
"""
{0} object created: {1}
"""

