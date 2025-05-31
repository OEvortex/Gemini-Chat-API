# -*- coding: utf-8 -*-
import os
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Union, Optional

from pydantic import BaseModel, field_validator
from curl_cffi import CurlError
from curl_cffi.requests import AsyncSession
from requests.exceptions import HTTPError, RequestException # Ensure RequestException is imported

from rich.console import Console

console = Console() # Instantiate console for logging

class Image(BaseModel):
    """
    Represents a single image object returned from Gemini.

    Attributes:
        url (str): URL of the image.
        title (str): Title of the image (default: "[Image]").
        alt (str): Optional description of the image.
        proxy (str | dict | None): Proxy used when saving the image.
        impersonate (str): Browser profile for curl_cffi to impersonate.
    """
    url: str
    title: str = "[Image]"
    alt: str = ""
    proxy: Optional[Union[str, Dict[str, str]]] = None
    impersonate: str = "chrome110"

    def __str__(self):
        return f"{self.title}({self.url}) - {self.alt}"

    def __repr__(self):
        short_url = self.url if len(self.url) <= 50 else self.url[:20] + "..." + self.url[-20:]
        short_alt = self.alt[:30] + "..." if len(self.alt) > 30 else self.alt
        return f"Image(title='{self.title}', url='{short_url}', alt='{short_alt}')"

    async def save(
        self,
        path: str = "downloaded_images",
        filename: Optional[str] = None,
        cookies: Optional[dict] = None,
        verbose: bool = False,
        skip_invalid_filename: bool = True,
    ) -> Optional[str]:
        """
        Save the image to disk using curl_cffi.
        Parameters:
            path: str, optional
                Directory to save the image (default "downloaded_images").
            filename: str, optional
                Filename to use; if not provided, inferred from URL.
            cookies: dict, optional
                Cookies used for the image request.
            verbose: bool, optional
                If True, outputs status messages (default False).
            skip_invalid_filename: bool, optional
                If True, skips saving if the filename is invalid.
        Returns:
            Absolute path of the saved image if successful; None if skipped.
        Raises:
            HTTPError if the network request fails.
            RequestException/CurlError for other network errors.
            IOError if file writing fails.
        """
        # Generate filename from URL if not provided
        if not filename:
            try:
                from urllib.parse import urlparse, unquote
                parsed_url = urlparse(self.url)
                base_filename = os.path.basename(unquote(parsed_url.path))
                # Remove invalid characters for filenames
                safe_filename = re.sub(r'[<>:"/\|?*]', '_', base_filename)
                if safe_filename and len(safe_filename) > 0:
                    filename = safe_filename
                else:
                    filename = f"image_{random.randint(1000, 9999)}.jpg"
            except Exception:
                filename = f"image_{random.randint(1000, 9999)}.jpg"

        # Validate filename length
        try:
            _ = Path(filename)
            max_len = 255
            if len(filename) > max_len:
                name, ext = os.path.splitext(filename)
                filename = name[:max_len - len(ext) - 1] + ext
        except (OSError, ValueError):
            if verbose:
                console.log(f"[yellow]Invalid filename generated: {filename}[/yellow]")
            if skip_invalid_filename:
                if verbose:
                    console.log("[yellow]Skipping save due to invalid filename.[/yellow]")
                return None
            filename = f"image_{random.randint(1000, 9999)}.jpg"
            if verbose:
                console.log(f"[yellow]Using fallback filename: {filename}[/yellow]")

        # Prepare proxy dictionary for curl_cffi
        proxies_dict = None
        if isinstance(self.proxy, str):
            proxies_dict = {"http": self.proxy, "https": self.proxy}
        elif isinstance(self.proxy, dict):
            proxies_dict = self.proxy

        try:
            # Use AsyncSession from curl_cffi
            async with AsyncSession(
                cookies=cookies,
                proxies=proxies_dict,
                impersonate=self.impersonate
                # follow_redirects is handled automatically by curl_cffi
            ) as client:
                if verbose:
                    console.log(f"Attempting to download image from: {self.url}")

                response = await client.get(self.url)
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get("content-type", "").lower()
                if "image" not in content_type and verbose:
                    console.log(f"[yellow]Warning: Content type is '{content_type}', not an image. Saving anyway.[/yellow]")

                # Create directory and save file
                dest_path = Path(path)
                dest_path.mkdir(parents=True, exist_ok=True)
                dest = dest_path / filename

                # Write image data to file
                dest.write_bytes(response.content)

                if verbose:
                    console.log(f"Image saved successfully as {dest.resolve()}")

                return str(dest.resolve())

        except HTTPError as e:
            console.log(f"[red]Error downloading image {self.url}: {e.response.status_code} {e}[/red]")
            raise
        except (RequestException, CurlError) as e:
            console.log(f"[red]Network error downloading image {self.url}: {e}[/red]")
            raise
        except IOError as e:
            console.log(f"[red]Error writing image file to {dest}: {e}[/red]")
            raise
        except Exception as e:
            console.log(f"[red]An unexpected error occurred during image save: {e}[/red]")
            raise


class WebImage(Image):
    """
    Represents an image retrieved from web search results.

    Returned when asking Gemini to "SEND an image of [something]".
    """
    pass

class GeneratedImage(Image):
    """
    Represents an image generated by Google's AI image generator (e.g., ImageFX).

    Attributes:
        cookies (dict[str, str]): Cookies required for accessing the generated image URL,
            typically from the GeminiClient/Chatbot instance.
    """
    cookies: Dict[str, str]

    # Updated validator for Pydantic V2
    @field_validator("cookies")
    @classmethod
    def validate_cookies(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Ensures cookies are provided for generated images."""
        if not v or not isinstance(v, dict):
            raise ValueError("GeneratedImage requires a dictionary of cookies from the client.")
        return v

    async def save(self, **kwargs) -> Optional[str]:
        """
        Save the generated image to disk.
        Parameters:
            filename: str, optional
                Filename to use. If not provided, a default name including
                a timestamp and part of the URL is used. Generated images
                are often in .png or .jpg format.
            Additional arguments are passed to Image.save.
        Returns:
            Absolute path of the saved image if successful, None if skipped.
        """
        if "filename" not in kwargs:
             ext = ".jpg" if ".jpg" in self.url.lower() else ".png"
             url_part = self.url.split('/')[-1][:10]
             kwargs["filename"] = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{url_part}{ext}"

        # Pass the required cookies and other args (like impersonate) to the parent save method
        return await super().save(cookies=self.cookies, **kwargs)
