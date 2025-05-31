# -*- coding: utf-8 -*-
import json
from pathlib import Path
from typing import Dict, Tuple, Union, Optional

from curl_cffi import CurlError
from curl_cffi.requests import AsyncSession
from requests.exceptions import RequestException, HTTPError, Timeout # Added Timeout

from rich.console import Console

# Assuming Endpoint and Headers enums are in 'enums.py' within the same package
from .enums import Endpoint, Headers

console = Console() # Instantiate console for logging

async def upload_file(
    file: Union[bytes, str, Path],
    proxy: Optional[Union[str, Dict[str, str]]] = None,
    impersonate: str = "chrome110"
) -> str:
    """
    Uploads a file to Google's Gemini server using curl_cffi and returns its identifier.

    Args:
        file (bytes | str | Path): File data in bytes or path to the file to be uploaded.
        proxy (str | dict, optional): Proxy URL or dictionary for the request.
        impersonate (str, optional): Browser profile for curl_cffi to impersonate. Defaults to "chrome110".

    Returns:
        str: Identifier of the uploaded file.

    Raises:
        HTTPError: If the upload request fails.
        RequestException: For other network-related errors.
        FileNotFoundError: If the file path does not exist.
    """
    # Handle file input
    if not isinstance(file, bytes):
        file_path = Path(file)
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found at path: {file}")
        with open(file_path, "rb") as f:
            file_content = f.read()
    else:
        file_content = file

    # Prepare proxy dictionary for curl_cffi
    proxies_dict = None
    if isinstance(proxy, str):
        proxies_dict = {"http": proxy, "https": proxy} # curl_cffi uses http/https keys
    elif isinstance(proxy, dict):
        proxies_dict = proxy # Assume it's already in the correct format

    try:
        # Use AsyncSession from curl_cffi
        async with AsyncSession(
            proxies=proxies_dict,
            impersonate=impersonate,
            headers=Headers.UPLOAD.value # Pass headers directly
            # follow_redirects is handled automatically by curl_cffi
        ) as client:
            response = await client.post(
                url=Endpoint.UPLOAD.value, # Use Endpoint enum
                files={"file": file_content},
            )
            response.raise_for_status() # Raises HTTPError for bad responses
            return response.text
    except HTTPError as e:
        console.log(f"[red]HTTP error during file upload: {e.response.status_code} {e}[/red]")
        raise # Re-raise HTTPError
    except (RequestException, CurlError) as e: # Catch CurlError as well
        console.log(f"[red]Network error during file upload: {e}[/red]")
        raise # Re-raise other request errors

def load_cookies(cookie_path: str) -> Tuple[str, str]:
    """
    Loads authentication cookies from a JSON file.

    Args:
        cookie_path (str): Path to the JSON file containing cookies.

    Returns:
        tuple[str, str]: Tuple containing __Secure-1PSID and __Secure-1PSIDTS cookie values.

    Raises:
        Exception: If the file is not found, invalid, or required cookies are missing.
    """
    try:
        with open(cookie_path, 'r', encoding='utf-8') as file: # Added encoding
            cookies = json.load(file)
        # Handle potential variations in cookie names (case-insensitivity)
        session_auth1 = next((item['value'] for item in cookies if item['name'].upper() == '__SECURE-1PSID'), None)
        session_auth2 = next((item['value'] for item in cookies if item['name'].upper() == '__SECURE-1PSIDTS'), None)

        if not session_auth1 or not session_auth2:
             raise StopIteration("Required cookies (__Secure-1PSID or __Secure-1PSIDTS) not found.")

        return session_auth1, session_auth2
    except FileNotFoundError:
        raise Exception(f"Cookie file not found at path: {cookie_path}")
    except json.JSONDecodeError:
        raise Exception("Invalid JSON format in the cookie file.")
    except StopIteration as e:
        raise Exception(f"{e} Check the cookie file format and content.")
    except Exception as e: # Catch other potential errors
        raise Exception(f"An unexpected error occurred while loading cookies: {e}")
