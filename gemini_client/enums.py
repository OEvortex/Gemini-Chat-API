# -*- coding: utf-8 -*-
from enum import Enum

class Endpoint(Enum):
    """
    Enum for Google Gemini API endpoints.

    Attributes:
        INIT (str): URL for initializing the Gemini session.
        GENERATE (str): URL for generating chat responses.
        ROTATE_COOKIES (str): URL for rotating authentication cookies.
        UPLOAD (str): URL for uploading files/images.
    """
    INIT = "https://gemini.google.com/app"
    GENERATE = "https://gemini.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate"
    ROTATE_COOKIES = "https://accounts.google.com/RotateCookies"
    UPLOAD = "https://content-push.googleapis.com/upload"

class Headers(Enum):
    """
    Enum for HTTP headers used in Gemini API requests.

    Attributes:
        GEMINI (dict): Headers for Gemini chat requests.
        ROTATE_COOKIES (dict): Headers for rotating cookies.
        UPLOAD (dict): Headers for file/image upload.
    """
    GEMINI = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        "Host": "gemini.google.com",
        "Origin": "https://gemini.google.com",
        "Referer": "https://gemini.google.com/",
        # User-Agent will be handled by curl_cffi impersonate
        # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-Same-Domain": "1",
    }
    ROTATE_COOKIES = {
        "Content-Type": "application/json",
    }
    UPLOAD = {"Push-ID": "feeds/mcudyrk2a4khkz"}

class Model(Enum):
    """
    Enum for available Gemini model configurations.

    Attributes:
        model_name (str): Name of the model.
        model_header (dict): Additional headers required for the model.
        advanced_only (bool): Whether the model is available only for advanced users.
    """
    # Updated model definitions based on reference implementation
    UNSPECIFIED = ("unspecified", {}, False)
    G_2_0_FLASH = (
        "gemini-2.0-flash",
        {"x-goog-ext-525001261-jspb": '[1,null,null,null,"f299729663a2343f"]'},
        False,
    )
    G_2_0_FLASH_THINKING = (
        "gemini-2.0-flash-thinking",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"7ca48d02d802f20a"]'},
        False,
    )
    G_2_5_FLASH = (
        "gemini-2.5-flash",
        {"x-goog-ext-525001261-jspb": '[1,null,null,null,"35609594dbe934d8"]'},
        False,
    )
    G_2_5_PRO = (
        "gemini-2.5-pro",
        {"x-goog-ext-525001261-jspb": '[1,null,null,null,"2525e3954d185b3c"]'},
        False,
    )
    G_2_0_EXP_ADVANCED = (
        "gemini-2.0-exp-advanced",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"b1e46a6037e6aa9f"]'},
        True,
    )
    G_2_5_EXP_ADVANCED = (
        "gemini-2.5-exp-advanced",
        {"x-goog-ext-525001261-jspb": '[null,null,null,null,"203e6bb81620bcfe"]'},
        True,
    )

    def __init__(self, name, header, advanced_only):
        """
        Initialize a Model enum member.

        Args:
            name (str): Model name.
            header (dict): Model-specific headers.
            advanced_only (bool): If True, model is for advanced users only.
        """
        self.model_name = name
        self.model_header = header
        self.advanced_only = advanced_only

    @classmethod
    def from_name(cls, name: str):
        """
        Get a Model enum member by its model name.

        Args:
            name (str): Name of the model.

        Returns:
            Model: Corresponding Model enum member.

        Raises:
            ValueError: If the model name is not found.
        """
        for model in cls:
            if model.model_name == name:
                return model
        raise ValueError(
            f"Unknown model name: {name}. Available models: {', '.join([model.model_name for model in cls])}"
        )
