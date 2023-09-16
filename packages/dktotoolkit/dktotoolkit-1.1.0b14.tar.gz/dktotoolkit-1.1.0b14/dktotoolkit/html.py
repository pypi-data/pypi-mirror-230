import html
import logging
import requests
import time
from typing import Optional

def _only_request(
        url: str,
        method: str,
        timeout: float,
        retry_timeout: bool,
        counter: int = 0,
        max_counter: int = 1
) -> requests.Response:
    """
    Perform a single HTTP request.

    :param url: The URL to request.
    :param method: The HTTP method to use (e.g., 'get', 'post').
    :param timeout: The timeout for the request in seconds.
    :param retry_timeout: Whether to retry if the request times out.
    :param counter: Counter for retry attempts.
    :param max_counter: Maximum number of retry attempts.
    :return: The HTTP response.
    """
    try:

        response = requests.request(url=url, method=method, timeout=timeout)
        response.raise_for_status()  # Raise an exception if the response contains an HTTP error code
        return response

    except requests.exceptions.Timeout:

        if retry_timeout and counter < max_counter:

            sleeping_time = timeout * 2**(counter + 1)
            logging.warning(f"Timed out ({timeout} s) {url}: retry {counter}/{max_counter} ; I'll wait {sleeping_time} s")
            time.sleep(sleeping_time)

            return _only_request(url=url, method=method, timeout=timeout*(counter+1), retry_timeout=retry_timeout, counter=counter+1, max_counter=max_counter)
        else:
            raise
        #

    except requests.exceptions.RequestException as e:
        logging.error(f"Error during request to {url}: {e}")
        raise
    #

def request_html_page(
        url: str,
        method: str = "get",
        timeout: float = 0.1,
        retry_timeout: bool = True,
        max_retries: int = 10,
        format_output:str = "html"
) -> str:
    """
    Request an HTML page and return its content as a string.

    :param str url: The URL of the HTML page.
    :param str method: The HTTP method to use (default is 'get').
    :param float timeout: The timeout for the request in seconds (default is 0.1 seconds).
    :param bool retry_timeout: Whether to retry if the request times out (default is True).
    :param int max_retries:  Maximum number of retry attempts.
    :param str format_output: Output format (html, json)
    :return: The HTML content as a string.
    """
    try:
        response = _only_request(url=url, method=method, timeout=timeout, retry_timeout=retry_timeout, max_counter=max_retries)
        response.raise_for_status()  # Raise an exception in case of an HTTP error code

        if format_output.lower() in ["html", "str"]:
            return html.unescape(response.text)
        elif format_output.lower() in ["json",]:
            return response.json()
        else:
            raise ValueError(f"format_output={format_output} not in [html, json]")
        #

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve HTML page from {url}: {e}")
        raise
    #
#


def read_html_file(path = "./index.html"):
    with open(path, 'r') as f:
        content = f.read()
    # endWith
    return html.unescape(content)
# endDef


