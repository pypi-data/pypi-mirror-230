# Tonita Python Library
This package contains the Tonita Python API. The API allows developers to upload a corpus of listings that each contain text and structured data, have Tonita build a search engine for the corpus, and perform search over it.

**This Python library is under active testing and development.**

## Documentation
See the *Tonita API docs*.

## Installation
The simplest way to install this library is by using `pip` from the command line:
```bash
pip install tonita
```

To install from source:
```bash
pip install .
```

## Getting started

### Terminology
The Tonita API has two basic concepts: **listings** and **corpora**.

1. **Listings** are the fundamental units over which search is performed; for a given query, the Tonita API will return the most relevant listings. Each listing has a unique ID that the developer decides, and each listing belongs to one or more corpora.

1. A **corpus** is a collection of listings. Each search request will perform search on listings in exactly one corpus. Corpora have unique IDs decided by the developer, and can be used to define groups of listings useful for the developer's use cases.

Developers have significant flexibility in the management of listings and corpora, including their creation, deletion, and modification. For more details, see the *Listings and corpora* section of the documentation.

### Providing an API key
Functions in this library make requests to Tonita's API server. In order for requests to be processed, an API key must be specified with each API call. (See the *Obtaining an API Key* section of the documentation to learn how to request an API key.) There are three ways to specify the API key when using the library:

1. Set the `TONITA_API_KEY` environment variable.
    ```bash
    export TONITA_API_KEY = "my-api-key"
    ```
    Upon importing the Tonita library, `tonita.api_key` will be set to this value.

2. Set the value of the `tonita.api_key` variable in Python after import:
    ```python
    import tonita
    tonita.api_key = "my-api-key"
    ```

    If the value of `tonita.api_key` is set using this method, it will overwrite the value of `tonita.api_key` provided by the environment variable `TONITA_API_KEY`.

3. Pass an `api_key` with each request. For example:
    ```python
    import tonita

    # Add a listing to a corpus.
    tonita.listings.add(
        json_path="path/to/data.json"
        corpus_id="my-corpus-id",
        api_key="my-api-key"
    )
    ```

    If an API key is provided this way, it will take precedence over both the value of `TONITA_API_KEY` and `tonita.api_key`. 

If an API key is not provided, a `TonitaAPIRequestError` will be raised.


### Providing a corpus ID

In addition to the API key, a corpus ID must also be provided for many requests (for example, when creating and deleting corpora, when working with listings, and when performing search).

There are two ways to set the corpus ID:

1. Set the value of the `tonita.corpus_id` variable in Python after import.
    ```python
    import tonita
    tonita.corpus_id = "my-corpus_id"
    ```

2. Pass a `corpus_id` with the request. For example:
    ```python
    import tonita
    from tonita.datatypes.search import SearchRequest

    tonita.api_key = "my-api-key"

    request = SearchRequest(
        query='sunny 1 bedroom on a quiet street near parks',
        max_results=20,
        categories=["manhattan", "brooklyn"],
        corpus_id="my-corpus-id"
    )
    
    tonita.search(request=request)
    ```
    
    If a corpus ID is provided this way, it will take precedence over the value of `tonita.corpus_id`.
    
If a corpus ID is not provided anywhere when calling a function that requires it, a `TonitaAPIRequestError` will be raised.

### Request and response types
Each function call will return a corresponding response object in the form of a [dataclass](https://docs.python.org/3/library/dataclasses.html). For example, a call to `tonita.listings.add()` will return an `AddListingsResponse` and a call to `tonita.search()` will return a `SearchResponse`.

When using `tonita.search()`, there is additionally a `SearchRequest` dataclass that must be passed in the API call.

See the docstrings in `tonita/datatypes` for details of the contents of each dataclass. For more details on these dataclasses, see the *Request and response types* section of the documentation.

### Error handling
There are a number of reasons why a function call may fail. When a call fails, a subclass of `tonita.errors.TonitaError` will be raised. Errors may be either client-side or server-side.

1. On the client side, a `TonitaBadRequestError` will be raised if the request is incorrectly formed in a way that can be caught before reaching the server. For example, this will happen if the API key is missing or if arguments are passed incorrectly.
2. Otherwise, the request is sent to the server. The server can then return errors in one of the following ways:
    1. If the request is malformed in a way that the server is unsure how to handle (e.g., an unrecognized field name or some other formatting error), a `TonitaBadRequestError` will be raised.
    2. If the API key is invalid or missing, a `TonitaUnauthorizedError` will be raised.
    3. If there is an internal server-side error (i.e., an error was encountered in the backend), a `TonitaInternalServerError` will be raised.
    4. If the server understands the request but it is an illegal request, an error message will be returned in the body of the response dataclass. For example, if a request is sent to delete a listing that does not exist, the resulting `DeleteListingsResponse` will have the success field set to `False` and the `error_message` field populated. It is up to the caller to handle these errors appropriately.

For details on errors and exceptions, see the *Errors and exceptions* section of the documentation.

## Examples
To use the Tonita library, you may first choose to set your API key.

```python
import tonita

tonita.api_key = "my-api-key"
```

See **Providing an API key** for other ways to set the API key.

### Adding data
First, create a corpus to add listings to:
```python
tonita.corpora.add(corpus_id="my-corpus-id")
```

This creates a corpus with the ID `my-corpus-id`. To confirm that it exists:
```python
response = tonita.corpora.exists(corpus_id="my-corpus-id")
assert response.exists 
```

Then add listings data to this corpus:
```python
tonita.corpus_id = "my-corpus-id"
tonita.listings.add(json_path="path/to/data.json")
tonita.listings.add(json_path="path/to/more_data.json")
```
See the *documentation* for details on the content and format of theses JSONs.

Finally, check their existence:
```python
tonita.listings.list()
```

Developers can also remove listings and corpora, and retrieve data for added listings. For the complete API, see the documentation.

### Performing search

To perform search, first create a `SearchRequest`, specifying the query string, the maximum number of results to return, and the categories to restrict the search to (if any). Then simply pass the `SearchRequest` to `tonita.search()`.

```python
from tonita.datatypes.search import SearchRequest

# Create the request dataclass.
request = SearchRequest(
    query='two bedroom with dishwasher a/c and bike room near dumbo',
    max_results=10,
    categories=["co-ops", "brooklyn"]
)

# Send the search request and receive the response.
response = tonita.search(request=request)
```

Since we set the API key and corpus IDs above, this search will be conducted for the account corresponding to the API key `"my-api-key"` and the corpus corresponding to `"my-corpus-id"`. That is, the above call is equivalent to:

```python
response = tonita.search(
    request=request,
    corpus_id="my-corpus-id",
    api_key="my-api-key"
)
```

This will return a `SearchResponse` containing listings relevant to the query. See `tonita/datatypes/search.py` for full details of what is returned.

## Advanced Usage
For better performance, users can create a single request session and reuse it for multiple requests. This is especially useful when adding many listings to a corpus.

Request Sessions are useful because they allow the underlying TCP connection to be reused, which can significantly improve performance. See the [requests documentation](https://requests.readthedocs.io/en/master/user/advanced/#session-objects) for more details.

This additional parameter is available only for the add method in the `tonita.listings` module and for the search method in the `tonita.search` module.

Example Usage:

```python
import tonita
import requests

# Create a session.
session = requests.Session()

tonita.listings.add(
    json_path="path/to/data.json",
    session=session
)
```

## Support

Please report bugs and other issues to [bugs@tonita.co](mailto:bugs@tonita.co) or file a Github Issue. Thank you in advance.
