from typing import Any
from strenum import StrEnum
from .exceptions import *


class ExceptionMsg:
    """
    Container class holding predefined error messages for the JokerAPI.co integration.

    Attributes:
    -----------
    INVALID_ACTIONNAME: str
        Error message indicating that an API Action name is not valid.

    REQUIRED_KEY : str
        Error message indicating that an API key must be set before attempting to dial or control call flow.

    INVALID_KEY : str
        Error message indicating that the provided API key is incorrect, resulting in the inability to dial or control call flow.

    INVALID_COUNTRY : str
        Error message indicating that the provided phone numbers may not be called.

    INVALID_PARAM : str
        Error message indicating that the keyword arguments aren't properly populated.
    
    UNKNOWN: str
        Error message indicating that the backend is experiencing an issue, and can't be translated.
    """
    INVALID_ACTIONNAME = "Internal Error, it seems like the API Action name provided is invalid."
    REQUIRED_KEY = "Please set an API key before processing to dial or control the flow of a call."
    INVALID_KEY = "The API key provided is invalid."
    INVALID_COUNTRY = "The 'to' or 'from' phone numbers are not whitelisted."
    INVALID_PARAM = "Please populate the keyword arguments correctly."
    UNKNOWN = "Your request has not been executed due to a issue via either JokerAPI or CDN, try again later."


class API(StrEnum):
    """
    Enum-like class `API` for building endpoint URLs and translating API actions into URLs for JokerAPI.co integration.

    Attributes:
    -----------
    URL : str
        The base URL template for constructing API endpoint URLs.

    Methods:
    --------
    __translator__(val: str, url: str, vars: dict) -> str:
        Translates the API action name into the corresponding endpoint URL with the provided variables.

    Parameters:
    -----------
    val : str
        The API action name, e.g., "DIAL", "PLAY", "TRANSFER", etc.

    url : str
        The base URL template.

    vars : dict
        A dictionary containing variables required for constructing the specific endpoint URL.

    Returns:
    --------
    str
        The translated endpoint URL for the given API action and variables.
    """
    URL = "https://api.jokerapi.co/voice/v1/{}?{}"

    def __translator__(val: str, 
                       url: str, 
                       vars: dict) -> str:
        """
        Translates API action name into the corresponding endpoint URL.
    
        Parameters:
        -----------
        val : str
            The API action name, e.g., "DIAL", "PLAY", "TRANSFER", etc.
    
        url : str
            The base URL template.
    
        vars : dict
            A dictionary containing variables required for constructing the specific endpoint URL.
    
        Returns:
        --------
        str
            The translated endpoint URL for the given API action and variables.
    
        Raises:
        -------
        INVALIDAPIACTIONNAME
            If the provided API action name is not recognized, this exception is raised with an error message.
        """
        url_templates = {
            "DIAL": "apikey={key}&to={to}&from={from}&webhookurl={url}",
            "PLAY": "apikey={key}&callsid={sid}&audiourl={audio_url}",
            "PLAYTEXT": "apikey={key}&callsid={sid}&text={text}&voice={voice}",
            "GATHER": "gather",
            "GATHERTEXT": "gathertext",
            "TRANSFER": "transfer",
            "HANGUP": "hangup"
        }
        if val in url_templates:
            return url.format(val.lower(), url_templates[val].format(**vars))
        
        raise INVALIDAPIACTIONNAME(ExceptionMsg.INVALID_ACTIONNAME)

class Joker(StrEnum):
    """
    An enumeration of responses registered and received from JokerAPI, utilized within the library to manage diverse responses.

    Attributes:
    -----------
    __unknown__ : list
        A list to collect unrecognized responses.

    UNKNOWN: str
        An unknown response which can't be translated.

    SUCCESS : str
        A response indicating that the operation was successful.
    
    PLAY_SUCCESS: str
        A response indicating that the operation to play audio was successful.
    
    PLAY_TEXT_SUCCESS: str
        A response indicating that the operating to play text was successful.

    INVALIDAUTH : str
        A response indicating an invalid API key, often leading to authorization failure.

    INVALIDPARAM : str
        A response indicating missing parameters in the request, leading to unsuccessful processing.

    SERVERFAILURE : str
        A response indicating a connection failure with the server.

    NO_BALANCE : str
        A response indicating insufficient balance for the requested action.

    INVALIDCOUNTRY : str
        A response indicating that the requested country is not whitelisted for the operation.

    GATHER_AUDIO : str
        A response indicating the playing of audio during the gathering phase.

    GATHER_TEXT : str
        A response indicating the playing of text during the gathering phase.

    CALL_ENDED : str
        A response indicating the termination of a call.

    PLAY_AUDIO : str
        A response indicating the playing of audio.

    PLAY_TEXT : str
        A response indicating the playing of text.

    TRANSFERING : str
        A response indicating the ongoing process of call transfer.

    Methods:
    --------
    __INVALID__(value: str) -> int:
        Register an unrecognized response and return its index in the '__unknown__' list.

    """
    __unknown__ = []

    UNKNOWN = "unknown"
    SUCCESS = "success"
    PLAY_SUCCESS = "playing audio"
    PLAY_TEXT_SUCCESS = "playing text"
    INVALIDAUTH = "invalid api key"
    INVALIDPARAM = "you are missing parameters"
    SERVERFAILURE = "Connection failed"
    NO_BALANCE = "you have no balance"
    INVALIDCOUNTRY = "this country is not whitelisted"

    GATHER_AUDIO = "playing audio while gathering"
    GATHER_TEXT = "playing text while gathering"

    CALL_ENDED = "call ended"

    PLAY_AUDIO = "playing audio"

    PLAY_TEXT = "playing text"

    TRANSFERING = "transfering call"

    def __INVALID__(value: str) -> tuple[Any, int]:
        """
        Register an unrecognized response and return its index in the '__unknown__' list.

        Parameters:
        -----------
        value : str
            The unrecognized response to register.

        Returns:
        --------
        tuple:
            0: any
                The assignment of the value appended to the __unknown__ array.

            1: int
                The index of the registered unrecognized response in the '__unknown__' list.
        """
        return (_ := Joker.__unknown__.append([value])), len(Joker.__unknown__)[-1]

translator: dict[Any] = {
    Joker.INVALIDAUTH: [INVALIDAPIKEY, ExceptionMsg.INVALID_KEY],
    Joker.INVALIDCOUNTRY: [INVALIDCOUNTRY, ExceptionMsg.INVALID_COUNTRY],
    Joker.INVALIDPARAM: [INVALIDPARAM, ExceptionMsg.INVALID_PARAM],
    Joker.UNKNOWN: [INVALIDRESPONSE, ExceptionMsg.UNKNOWN]
}
