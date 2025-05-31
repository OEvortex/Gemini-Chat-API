from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gemini-client-api",
    version="0.1.0",
    author="AI Agent Contributor", # Generic author
    author_email="contributor@example.com", # Generic email
    description="A Python client for interacting with Google's Gemini API using curl_cffi.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/gemini-client-api",  # Generic repository URL
    packages=find_packages(where=".", include=["gemini_client", "gemini_client.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7", # Based on f-strings, asyncio, pydantic v2 features
    install_requires=[
        "curl_cffi>=0.5.9",
        "pydantic>=2.0",
        "rich>=10.0",
        "requests>=2.20",
    ],
    keywords="gemini google ai api client curl_cffi async",
    project_urls={
        "Bug Reports": "https://github.com/example/gemini-client-api/issues", # Generic issue URL
        "Source": "https://github.com/example/gemini-client-api", # Generic source URL
    },
)
