# Gemini Client API

This Python package provides a client for interacting with Google's Gemini API. It is built using `curl_cffi` for efficient and impersonated HTTP requests.

## Features

- Asynchronous support using `asyncio`.
- Synchronous wrapper for ease of use.
- Conversation management (save, load).
- File and image uploading.
- Support for various Gemini models.
- Image object handling (WebImage, GeneratedImage) with save functionality.
- Proxy support.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```
2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
    (Ensure `requirements.txt` includes `curl_cffi`, `pydantic`, and `rich`.)

    Alternatively, if a `setup.py` is provided:
    ```bash
    pip install .
    ```

## Usage

### Prerequisites

You need to obtain your `__Secure-1PSID` and `__Secure-1PSIDTS` cookies from Google Gemini.

1.  Go to [https://gemini.google.com/app](https://gemini.google.com/app)
2.  Open your browser's developer tools (usually by pressing F12).
3.  Go to the "Application" (or "Storage") tab.
4.  Under "Cookies" -> "https://gemini.google.com", find the `__Secure-1PSID` and `__Secure-1PSIDTS` cookies.
5.  Create a JSON file (e.g., `cookies.json`) with the following format:

    ```json
    [
        {
            "name": "__Secure-1PSID",
            "value": "YOUR___SECURE-1PSID_VALUE_HERE"
        },
        {
            "name": "__Secure-1PSIDTS",
            "value": "YOUR___SECURE-1PSIDTS_VALUE_HERE"
        }
    ]
    ```

### Synchronous Chatbot

```python
from gemini_client import Chatbot, Model

# Initialize the chatbot
try:
    chatbot = Chatbot(cookie_path="cookies.json", model=Model.G_2_5_PRO)
except Exception as e:
    print(f"Error initializing chatbot: {e}")
    exit()

# Ask a question
try:
    response = chatbot.ask("Hello, how are you today?")
    if response and not response.get("error"):
        print("Gemini:", response["content"])

        # Handling images in response
        if response.get("images"):
            print("\nImages found:")
            for img_data in response["images"]:
                # Note: The 'images' in the response are dicts.
                # To use the Image class features (like saving), you'd typically
                # instantiate Image objects from these dicts if needed,
                # especially if you want to use the save method directly on an Image object.
                # For generated images, you'd need to pass cookies to GeneratedImage.
                print(f"- Title: {img_data.get('title', '[Image]')}, URL: {img_data.get('url')}, Alt: {img_data.get('alt')}")
    else:
        print("Error or no content in response:", response)

except Exception as e:
    print(f"Error during ask: {e}")

# Ask a question with an image
try:
    # Ensure 'image.png' exists or provide a valid path/bytes
    response_with_image = chatbot.ask("What is in this image?", image="path/to/your/image.png")
    if response_with_image and not response_with_image.get("error"):
        print("\nGemini (with image):", response_with_image["content"])
    else:
        print("Error or no content in response with image:", response_with_image)
except FileNotFoundError:
    print("Image file not found. Skipping ask with image example.")
except Exception as e:
    print(f"Error during ask with image: {e}")

# Save a conversation
chatbot.save_conversation("conversations.json", "my_chat_session")
print("\nConversation 'my_chat_session' saved.")

# Load a conversation
if chatbot.load_conversation("conversations.json", "my_chat_session"):
    print("Conversation 'my_chat_session' loaded.")
    # Continue chatting in the loaded conversation
    response_continued = chatbot.ask("What was our last topic?")
    if response_continued and not response_continued.get("error"):
        print("Gemini (continued):", response_continued["content"])
    else:
        print("Error or no content in continued response:", response_continued)
```

### Asynchronous Chatbot

```python
import asyncio
from gemini_client import AsyncChatbot, Model
from gemini_client.utils import load_cookies # For loading cookies explicitly

async def main():
    try:
        secure_1psid, secure_1psidts = load_cookies("cookies.json")
        async_chatbot = await AsyncChatbot.create(
            secure_1psid=secure_1psid,
            secure_1psidts=secure_1psidts,
            model=Model.G_2_5_PRO
        )
    except Exception as e:
        print(f"Error initializing async chatbot: {e}")
        return

    # Ask a question
    try:
        response = await async_chatbot.ask("Hello, asynchronously!")
        if response and not response.get("error"):
            print("Gemini (async):", response["content"])
        else:
            print("Error or no content in async response:", response)
    except Exception as e:
        print(f"Error during async ask: {e}")

    # Example of saving an image if one was returned and properly parsed into an Image object
    # This part is illustrative, actual image saving depends on how you handle the response['images']
    # if response and response.get("images"):
    #     from gemini_client import WebImage # or GeneratedImage
    #     first_image_data = response["images"][0]
    #     # Assuming it's a web image for this example
    #     img_obj = WebImage(url=first_image_data["url"], title=first_image_data.get("title"), alt=first_image_data.get("alt"))
    #     # For GeneratedImage, you would need:
    #     # img_obj = GeneratedImage(url=..., cookies=async_chatbot.session.cookies.get_dict())
    #     try:
    #         saved_path = await img_obj.save(path="downloaded_async_images", verbose=True)
    #         if saved_path:
    #             print(f"Image saved to: {saved_path}")
    #     except Exception as e:
    #         print(f"Error saving image: {e}")

    # Close the session when done (important for AsyncSession)
    await async_chatbot.session.close()

if __name__ == "__main__":
    # Example of how to run the async main function
    # In a real application, you might use asyncio.run(main())
    # For simplicity in this README, we'll just call it if this script itself was run.
    # To run this example:
    # 1. Save this code as a Python file (e.g., example_async.py)
    # 2. Ensure cookies.json is present
    # 3. Run `python example_async.py`
    #
    # For this README, we'll just define it.
    # To run:
    # loop = asyncio.get_event_loop()
    # try:
    #     loop.run_until_complete(main())
    # except KeyboardInterrupt:
    #     print("Exiting...")
    # finally:
    #     # Clean up any pending tasks
    #     for task in asyncio.all_tasks(loop):
    #         task.cancel()
    #     try:
    #         loop.run_until_complete(loop.shutdown_asyncgens())
    #     finally:
    #         loop.close()
    pass # Placeholder for running the async main if this were a runnable script
```

## Modules

The package is structured as follows:

-   `gemini_client/`: Main package directory.
    -   `__init__.py`: Makes the directory a package and exports key components.
    -   `core.py`: Contains `Chatbot` and `AsyncChatbot` classes.
    -   `enums.py`: Defines `Endpoint`, `Headers`, and `Model` enums.
    -   `images.py`: Defines `Image`, `WebImage`, and `GeneratedImage` classes for image handling.
    -   `utils.py`: Contains utility functions like `upload_file` and `load_cookies`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
