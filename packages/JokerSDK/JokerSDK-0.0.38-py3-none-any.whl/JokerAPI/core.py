import httpx, asyncio, re
from .enums import API, ExceptionMsg, Joker, translator
from typing import Any, Awaitable
from .exceptions import *


class Number:
    """
    Represents a valid phone number.

    This class is used to store and work with phone numbers in a standardized format.

    Parameters:
    -----------
    number (str):
        The phone number as a string, optionally including the '+' sign.

    Attributes:
    -----------
    number (str):
        The formatted phone number without the '+' sign.
    """
    def __init__(self, 
                 number: str
                 ) -> None:
        """
        Initialize a Number instance.

        Parameters:
        -----------
        number (str):
            The phone number as a string.
        """
        self.number: str = number.strip("+").strip(" ")

class JokerMethod:
    """
    JokerMethod class for interacting with the JokerAPI.co voice API.

    This class provides methods for initiating outbound calls using the JokerAPI.co voice API.

    Parameters:
    -----------
    api_key (str, optional):
        The API key for authenticating API requests.

    Methods:
    --------
    run_async(func: Awaitable[None], *args, **kwargs) -> None:
        Run an asynchronous function using asyncio's event loop.

        This function takes an asynchronous function as an argument and runs it within asyncio's event loop.

        Parameters:
        -----------
        func (Awaitable[None]):
            The asynchronous function to be executed.

        Returns:
        --------
        None

    dial(dial_to: Number, dial_from: Number, callback_url: str = "https://0.0.0.0/*", **kwargs) -> str:
        Initiate an outbound call using the JokerAPI.co voice API.

        This method creates and handles API requests to the 'voice/v1/dial' endpoint via JokerAPI.co.

        Parameters:
        -----------
        dial_to (Number):
            The destination phone number to dial.
        dial_from (Number):
            The caller ID to display when dialing the destination number.
        callback_url (str, optional):
            The URL where status change notifications are sent, corresponding to the user's API callback server.
            Default is "https://0.0.0.0/*".
        **kwargs (dict, optional):
            Additional optional parameters:
            - request_method (str):
                The HTTP method for the API request (default is 'GET', supports 'GET' or 'POST').
            - proxy (str or dict):
                Proxy configuration for the API request.
                Examples: 'all', 'all://*api.jokerapi.co', 'http://', 'https://',
                {"http": "USERNAME:PASSWORD@DOMAIN:PORT", "https": "USERNAME:PASSWORD@DOMAIN:PORT"}.

        Returns:
        --------
        str:
            The Session ID of the channel, which uniquely identifies the initiated call.

        Raises:
        -------
        REQUIREDAPIKEY:
            If the API key is missing.
        INVALIDAPIKEY:
            If the API key is invalid.
        INVALIDCOUNTRY:
            If the dial_to or dial_from phone numbers aren't whitelisted.
        INVALIDPARAM:
            If the keyword arguments aren't populated correctly.

        Notes:
        ------
        - Ensure that your JokerAPI.co API key is set using the `api_key` attribute of the `JokerMethod` instance before calling this method.
        - Make sure that the provided phone numbers are correctly formatted using the `Number` class.
    """
    def __init__(self, 
                 api_key: str = False, 
                 **kwargs
                 ) -> None:
        self.api_key: str = api_key

    def dial(self, 
            dial_to: Number, 
            dial_from: Number, 
            callback_url: str = "https://0.0.0.0/*", 
            **kwargs
            ) -> str:
        """
        Initiate an outbound call using the JokerAPI.co voice API.

        This method creates and handles API requests to the 'voice/v1/dial' endpoint via JokerAPI.co.

        Parameters:
        -----------
        dial_to (Number):
            The destination phone number to dial.
        dial_from (Number):
            The caller ID to display when dialing the destination number.
        callback_url (str, optional):
            The URL where status change notifications are sent, corresponding to the user's API callback server.
            Default is "https://0.0.0.0/*".
        **kwargs (dict, optional):
            Additional optional parameters:
            - request_method (str):
                The HTTP method for the API request (default is 'GET', supports 'GET' or 'POST').
            - proxy (str or dict):
                Proxy configuration for the API request.
                Examples: 'all', 'all://*api.jokerapi.co', 'http://', 'https://',
                {"http": "USERNAME:PASSWORD@DOMAIN:PORT", "https": "USERNAME:PASSWORD@DOMAIN:PORT"}.

        Returns:
        --------
        str:
            The Session ID of the channel, which uniquely identifies the initiated call.

        Raises:
        -------
        REQUIREDAPIKEY:
            If the API key is missing.
        INVALIDAPIKEY:
            If the API key is invalid.
        INVALIDCOUNTRY:
            If the dial_to or dial_from phone numbers aren't whitelisted.
        INVALIDPARAM:
            If the keyword arguments aren't populated correctly.

        Notes:
        ------
        - Ensure that your JokerAPI.co API key is set using the `api_key` attribute of the `JokerMethod` instance before calling this method.
        - Make sure that the provided phone numbers are correctly formatted using the `Number` class.
        """
        if not self.api_key:
            raise REQUIREDAPIKEY(ExceptionMsg.REQUIRED_KEY)

        response = httpx.request(
            "GET" if not kwargs.get("request_method", False) else kwargs['request_method'] if kwargs['request_method'] in ["GET", "POST"] else "GET",
            API.__translator__("DIAL", API.URL, {"key": self.api_key, "to": dial_to.number, "from": dial_from.number, "url": callback_url}),
            proxies=None if not kwargs.get("proxy", False) else kwargs['proxy'] if isinstance(kwargs['proxy'], dict) else None,
            headers={"User-Agent": "JokerSDK [VDM@v0.0.37]", "X-J-SDK-CLIENT": "JokerSDK/API"}
        ).json()

        if response.get("context", False) and not response['context'] == Joker.SUCCESS:
            raise translator[response['context']][0](translator[response['context']][1])
        
        elif not response.get("context", False) and not isinstance(response['callsid'], str):
            raise translator[Joker.UNKNOWN][0](translator[Joker.UNKNOWN][1])
        else:
            return response['callsid']

    def play(self,
             sid: str,
             audio_url: str,
             **kwargs) -> str:
        """
        Initiate an outbound call using the JokerAPI.co voice API.

        This method creates and handles API requests to the 'voice/v1/play' endpoint via JokerAPI.co.

        Parameters:
        -----------
        sid (str):
            The Call Session Identifier given when a successful call is initiated.
        audio_url (str):
            The URL of the audio file to play into the channel.
        **kwargs (dict, optional):
            Additional optional parameters:
            - request_method (str):
                The HTTP method for the API request (default is 'GET', supports 'GET' or 'POST').
            - proxy (str or dict):
                Proxy configuration for the API request.
                Examples: 'all', 'all://*api.jokerapi.co', 'http://', 'https://',
                {"http": "USERNAME:PASSWORD@DOMAIN:PORT", "https": "USERNAME:PASSWORD@DOMAIN:PORT"}.
        """
        if not self.api_key:
            raise REQUIREDAPIKEY(ExceptionMsg.REQUIRED_KEY)
        
        response = httpx.request(
            "GET" if not kwargs.get("request_method", False) else kwargs['request_method'] if kwargs['request_method'] in ["GET", "POST"] else "GET",
            API.__translator__("PLAY", API.URL, {"key": self.api_key, "sid": sid, "audio_url": audio_url}),
            proxies=None if not kwargs.get("proxy", False) else kwargs['proxy'] if isinstance(kwargs['proxy'], dict) else None,
            headers={"User-Agent": "JokerSDK [VDM@v0.0.37]", "X-J-SDK-CLIENT": "JokerSDK/API"}
        ).json()

        if response.get("context", False) and not response['context'] == Joker.PLAY_SUCCESS:
            raise translator[response['context']][0](translator[response['context']][1])
        else:
            return sid

    def play_text(self,
                  sid: str,
                  text: str,
                  voice: str = "🇺🇸 Joanna",
                  **kwargs) -> str:
        
        if not self.api_key:
            raise REQUIREDAPIKEY(ExceptionMsg.REQUIRED_KEY)

        response = httpx.request(
            "GET" if not kwargs.get("request_method", False) else kwargs['request_method'] if kwargs['request_method'] in ["GET", "POST"] else "GET",
            API.__translator__("PLAYTEXT", API.URL, {"key": self.api_key, "text": text, "voice": voice, "sid": sid}),
            proxies=None if not kwargs.get("proxy", False) else kwargs['proxy'] if isinstance(kwargs['proxy'], dict) else None,
            headers={"User-Agent": "JokerSDK [VDM@v0.0.37]", "X-J-SDK-CLIENT": "JokerSDK/API"}
        ).json()

        if response.get("context", False) and not response['context'] == Joker.SUCCESS:
            raise translator[response['context']][0](translator[response['context']][1])
        else:
            return response['callsid']
