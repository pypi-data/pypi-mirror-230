"""
Module: xprlogininfo.py

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
from .xprauthenticationtype import XPRAuthenticationType

# auto-generate the "__all__" variable with classes decorated with "@export".
from .xprutils import export


@export
class XPRLoginInfo:
    """
    Login information returned by a successful call to the LoginBasicUser 
    or LoginWindowsUser call.
    
    Threadsafety:
        This class is fully thread-safe.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the class.
        """
        # initialize instance.
        self._fAuthenticationType:XPRAuthenticationType = XPRAuthenticationType.Unknown
        self._fExpireTime:datetime = None
        self._fPassword:str = None
        self._fRegistrationTime:datetime = None
        self._fScope:str = None
        self._fTimeToLiveLimited:bool = False
        self._fTimeToLiveSeconds:int = 0
        self._fToken:str = None
        self._fTokenType:str = None
        self._fUserName:str = None


    @property
    def AuthenticationType(self) -> XPRAuthenticationType:
        """ 
        Type of user credentials used (e.g. Basic, Windows, etc) in the authentication process.

        Returns:
            The AuthenticationType property value.
        """
        return self._fAuthenticationType

    @AuthenticationType.setter
    def AuthenticationType(self, value:XPRAuthenticationType) -> None:
        """ 
        Sets the AuthenticationType property value.
        """
        if value != None:
            self._fAuthenticationType = value


    @property
    def ExpireTime(self) -> datetime:
        """ 
        Date and Time (UTC) at which the security token willl expire.

        Returns:
            The ExpireTime property value.

        This value is calculated by adding the TimeToLive property value to the 
        RegistrationTime property value.
        """
        return self._fExpireTime

    @ExpireTime.setter
    def ExpireTime(self, value:datetime) -> None:
        """ 
        Sets the ExpireTime property value.
        """
        if value != None:
            self._fExpireTime = value


    @property
    def Password(self) -> str:
        """ 
        Security password which is used in subsequent calls to the REST server 
        for authentication.

        Returns:
            The Password property value.
        """
        return self._fPassword

    @Password.setter
    def Password(self, value:str) -> None:
        """ 
        Sets the Password property value.
        """
        if value != None:
            self._fPassword = value


    @property
    def RegistrationTime(self) -> datetime:
        """ 
        Time at which the security token was registered, in UTC format.

        Returns:
            The RegistrationTime property value.
        """
        return self._fRegistrationTime

    @RegistrationTime.setter
    def RegistrationTime(self, value:datetime) -> None:
        """ 
        Sets the RegistrationTime property value.
        """
        if value != None:
            self._fRegistrationTime = value


    @property
    def Scope(self) -> str:
        """ 
        Security Scope which the token is to be used for (e.g. "managementserver", etc).

        Returns:
            The Scope property value.
        """
        return self._fScope

    @Scope.setter
    def Scope(self, value:str) -> None:
        """ 
        Sets the Scope property value.
        """
        if value != None:
            self._fScope = value


    @property
    def TimeToLiveLimited(self) -> bool:
        """ 
        TimeToLive calculated using time profile from APPLICATIONACCESSCLIENTLOGIN attribute.

        Returns:
            The TimeToLiveLimited property value.
        """
        return self._fTimeToLiveLimited

    @TimeToLiveLimited.setter
    def TimeToLiveLimited(self, value:bool) -> None:
        """ 
        Sets the TimeToLiveLimited property value.
        """
        if value != None:
            self._fTimeToLiveLimited = value

    
    @property
    def TimeToLiveMilliseconds(self) -> int:
        """ 
        Remaining time (in milliseconds) to live for the security token.

        Returns:
            The TimeToLiveSeconds property value, converted to milliseconds.
        """
        if (self._fTimeToLiveSeconds != None):
            # convert token expire time to milliseconds to match web-services format.
            return self._fTimeToLiveSeconds * 1000


    @property
    def TimeToLiveSeconds(self) -> int:
        """ 
        Remaining time (in seconds) to live for the security token.

        Returns:
            The TimeToLiveSeconds property value.
        """
        return self._fTimeToLiveSeconds

    @TimeToLiveSeconds.setter
    def TimeToLiveSeconds(self, value:int) -> None:
        """ 
        Sets the TimeToLiveSeconds property value.
        """
        if value != None:
            self._fTimeToLiveSeconds = value


    @property
    def Token(self) -> str:
        """ 
        Security token which is used in subsequent calls to the REST server 
        for authentication.

        Returns:
            The Token property value.
        """
        return self._fToken

    @Token.setter
    def Token(self, value:str) -> None:
        """ 
        Sets the Token property value.
        """
        if value != None:
            self._fToken = value


    @property
    def TokenType(self) -> str:
        """ 
        Security Token Type (e.g. "Bearer", etc).

        Returns:
            The TokenType property value.
        """
        return self._fTokenType

    @TokenType.setter
    def TokenType(self, value:str) -> None:
        """ 
        Sets the TokenType property value.
        """
        if value != None:
            self._fTokenType = value


    @property
    def UserName(self) -> str:
        """ 
        Security username which is used in subsequent calls to the REST server 
        for authentication.

        Returns:
            The UserName property value.
        """
        return self._fUserName

    @UserName.setter
    def UserName(self, value:str) -> None:
        """ 
        Sets the UserName property value.
        """
        if value != None:
            self._fUserName = value


    def __str__(self) -> str:
        """
        Returns a string representation of the object.
        
        Returns:
            A string in the form of "User Name: {1} ({0} Account Type)\nToken Expires: {2} (UTC)\nToken Value:\n{3}"
        """
        return "\
User Name: {1} ({0} Account Type)\n\
Token Expires: {2} (UTC)\n\
Token Value:\n{3}".format(self.AuthenticationType, 
                          self.UserName, 
                          self.ExpireTime.strftime("%Y-%m-%d %H:%M:%S"), 
                          self.Token)
