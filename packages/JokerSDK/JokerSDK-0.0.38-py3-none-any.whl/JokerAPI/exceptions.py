class INVALIDAPIACTIONNAME(Exception):
    """
    Exception raised when a API Action name is not correct, meaning;
    The API action name doesn't exist in the Joker API end points, it's not a correct functionality.
    """
    
class REQUIREDAPIKEY(Exception):
    """
    Exception raised when an API key is not provided for a required operation.

    This exception is raised when an API key is expected but not provided, preventing the execution of certain actions.
    """

class INVALIDAPIKEY(Exception):
    """
    Exception raised when an API key is invalid, usually indicating authorization failure.

    This exception is raised when the provided API key is incorrect or unauthorized, leading to inability to perform
    authorized actions such as dialing or controlling call flow.
    """

class INVALIDCOUNTRY(Exception):
    """
    Exception raised when the polluted argument are not whitelisted by the Voice API.

    This exception is raised when the 'to' or 'from' integer values are not allowed to be called to by the API.
    """

class INVALIDPARAM(Exception):
    """
    Exception raised when the API request operation has not been polluted properly.
    
    This exception may be raised required key word arguments are not properly polluted or not polluted at all.
    """

class INVALIDRESPONSE(Exception):
    """
    Exception raised when the API request has either not responded with a valid entity or has not responded at all.
    
    This exception may be raised if the Joker API or CDN is unavailable.
    """