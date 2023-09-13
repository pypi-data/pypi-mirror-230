# CustomSession

## Overview

CustomSession is a Python package that provides a flexible and customizable HTTP client for making synchronous and
asynchronous HTTP requests. This package is built on top of the popular HTTP client librarys, httpx and requests, and
offers several features to simplify and enhance your HTTP requests.

## Features

1. **Synchronous and Asynchronous Support**: CustomSession provides both synchronous and asynchronous HTTP clients

2. **Random User-Agent**: Randomly generated desktop user-agent for all requests sent by an HTTP client

3. **Proxy Support**: CustomSession allows you to specify an HTTP/s proxy for all requests sent by an HTTP client

4. **Retry Mechanism**: Configure the number of retries for each request to handle exceptions gracefully.

5. **Exception Handling**: Customize the exceptions to be ignored during retries, allowing you to manage specific error
   conditions.

6. **Session Metadata**: Store and manage miscellaneous session data as a dictionary, making it easier to maintain
   context between requests.

## Installation

You can install CustomSession using pip:

```bash
$ pip install custom-session
```

## Usage

### Synchronous Client

Here's how you can use CustomSession synchronously:

```python
from CustomSession import SyncSession

# Create a synchronous session
with SyncSession() as session:
    response = session.get('https://example.com')
    print(response.text)
```

Read more [here](#syncsession)

### Asynchronous Client

To use CustomSession asynchronously, you use it within an asynchronous context:

```python
import asyncio
from CustomSession import AsyncSession


async def main():
    async with AsyncSession() as session:
        response = await session.get('https://example.com')
        print(response.text)


# Run the asynchronous code
loop = asyncio.run(main())
```

Read more [here](#asyncsession)


### API Reference

#### SyncSession

##### Overview

`SyncSession` is an synchronous HTTP client class in Python, inherited from `requests.Session`
from [requests](https://github.com/psf/requests). It is designed to simplify making HTTP requests with features such as
maintaining a unique user-agent, handling metadata, and optional proxy support.   
This class is particularly useful for building synchronous web scraping or web automation scripts.

##### Usage

To use the `SyncSession` class, you should first import it and then create an instance of it. You can customize the
behavior of the session by passing optional parameters during initialization.

```python
from CustomSession import SyncSession

# Create an instance of SyncSession
session = SyncSession(proxy="1.1.1.1", ignore_exceptions=(Exception,))
```

##### Parameters

- `proxy` (optional): Specifies an HTTP/s proxy to use when sending requests.
- `ignore_exceptions` (optional): A tuple of exceptions to be ignored when sending requests. If an exception specified
  in this tuple occurs during a request, it will be caught, and the request will be retried.
- `user_agent` (UserAgent, optional): A user agent for the session. Default is a randomly generated user agent for a
  desktop device.
- `meta_data` (SessionMetaData | dict, optional): Additional metadata for the session. Default is an instance
  of `SessionMetaData` or an empty dictionary.

##### Methods

SyncSession provides several asynchronous HTTP request methods,
including `get`, `post`, `put`, `delete`, `patch`, `head`, and `options`. These methods allow you to make various types
of HTTP requests and handle retries automatically in case of specified exceptions.

- `get`: Sends an HTTP GET request.

- `post`: Sends an HTTP POST request.

- `put`: Sends an HTTP PUT request.

- `delete`: Sends an HTTP DELETE request.

- `patch`: Sends an HTTP PATCH request.

- `head`: Sends an HTTP HEAD request.

- `options`: Sends an HTTP OPTIONS request.

Each of these methods accepts parameters for request configuration and allows you to specify the number of retries in
case of exceptions.

##### Example

Here is an example of how to use the `SyncSession` class to send a GET request:

```python
from CustomSession import SyncSession

# Create an instance of SyncSession
session = SyncSession()

# Send a GET request
response = session.get("https://example.com")

# Check the response status code
if response.status_code == 200:
    print("Request was successful")
else:
    print("Request failed")
```

##### Exception Handling

The `SyncSession` class handles exceptions during HTTP requests by retrying the request up to the specified number of
times (`retries` parameter) if the exception matches any of the types listed in `ignore_exceptions`. If the maximum
number of retries is reached, it raises a `RetriesExceeded` exception with an error message indicating the number of
failed attempts.

Please make sure to handle `RetriesExceeded` exceptions appropriately in your code.

```python
from CustomSession import SyncSession, RetriesExceeded

session = SyncSession()
try:
    response = session.get("https://example.com", retries=5)
    print("Request was successful")
except RetriesExceeded as e:
    print(f"Request failed after {e.retries_attempted} attempts")

```

#### AsyncSession

##### Overview

`AsyncSession` is an asynchronous HTTP client class in Python, inherited from `httpx.AsyncClient`
from [httpx](https://github.com/encode/httpx/). It is designed to simplify making HTTP requests with features such as
maintaining a unique user-agent, handling metadata, and optional proxy support.   
This class is particularly useful for building asynchronous web scraping or web automation scripts.

##### Usage

To use the `AsyncSession` class, you can create an instance of it using the `async with` statement, which allows you to
manage the lifecycle of the client. Here's a basic example of how to use it:

```python
import asyncio
from CustomSessions import AsyncSession


async def main():
    async with AsyncSession() as client:
        response = await client.get('https://example.org')
        print(response.text)


if __name__ == "__main__":
    asyncio.run(main())
```

##### Parameters

The `AsyncSession` class accepts several optional parameters:

- `proxy` (optional): Specifies an HTTP/s proxy to use when sending requests.

- `ignore_exceptions` (optional): A tuple of exceptions to be ignored when sending requests. If an exception specified
  in this tuple occurs during a request, it will be caught, and the request will be retried.

- `auth` (optional): An authentication class to use when sending requests. This allows you to provide authentication
  credentials for requests, such as username and password.

- `meta_data` (optional): A dictionary or an instance of `SessionMetaData` that can be used to store miscellaneous
  session data. This data persists across requests and can be useful for storing session-specific information.

##### Methods

AsyncSession provides several asynchronous HTTP request methods,
including `get`, `post`, `put`, `delete`, `patch`, `head`, and `options`. These methods allow you to make various types
of HTTP requests and handle retries automatically in case of specified exceptions.

- `get`: Sends an HTTP GET request.

- `post`: Sends an HTTP POST request.

- `put`: Sends an HTTP PUT request.

- `delete`: Sends an HTTP DELETE request.

- `patch`: Sends an HTTP PATCH request.

- `head`: Sends an HTTP HEAD request.

- `options`: Sends an HTTP OPTIONS request.

Each of these methods accepts parameters for request configuration and allows you to specify the number of retries in
case of exceptions.

##### Example

Here's an example of using the `get` method with retries:

```python
async with AsyncSession() as client:
    response = await client.get('https://example.org', retries=3)
    if response.status_code == 200:
        print(response.text)
        else:
        print("Request failed")
```

In this example, the `get` method is used to make a GET request to [https://example.org](https://example.org/), and it
will retry up to 3 times if certain exceptions specified in the `ignore_exceptions` parameter occur.

##### Exception Handling

The `AsyncSession` class handles exceptions during HTTP requests by retrying the request up to the specified number of
times (`retries` parameter) if the exception matches any of the types listed in `ignore_exceptions`. If the maximum
number of retries is reached, it raises a `RetriesExceeded` exception with an error message indicating the number of
failed attempts.

Please make sure to handle `RetriesExceeded` exceptions appropriately in your code.

```python
from CustomSession import AsyncSession, RetriesExceeded

session = AsyncSession()
try:
    async with AsyncSession() as client:
        response = await client.get("https://example.com", retries=5)
print("Request was successful")
except RetriesExceeded as e:
print(f"Request failed after {e.retries_attempted} attempts")

```