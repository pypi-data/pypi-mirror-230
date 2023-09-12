import pytest
from unittest.mock import patch
from pygethub.paginator import (
    fetch,
    get_next_page_url,
    PaginatedGitHubResource
)

def test_get_next_page_url_with_next_url():
    # Prepare a link header with a next URL
    link_header = '<https://api.github.com/users?page=2>; rel="next", <https://api.github.com/users?page=5>; rel="last"'
    # Call the function
    result = get_next_page_url(link_header)
    # Check the result
    assert result == 'https://api.github.com/users?page=2'

def test_get_next_page_url_without_next_url():
    # Prepare a link header without a next URL
    link_header = '<https://api.github.com/users?page=1>; rel="prev", <https://api.github.com/users?page=5>; rel="last"'
    # Call the function
    result = get_next_page_url(link_header)
    # Check the result
    assert result is None

def test_get_next_page_url_with_none_link_header():
    # Prepare a None link header
    link_header = None
    # Call the function
    result = get_next_page_url(link_header)
    # Check the result
    assert result is None

@patch('pygethub.resources.fetch', autospec=True)
@patch('pygethub.paginator.get_next_page_url', autospec=True)
def test_no_more_data(mock_get_next_page_url, mock_fetch):
    # Mock the fetch function to return no data
    mock_fetch.return_value = {"data": [], "link": None}
    # Mock the get_next_page_url function to return None
    mock_get_next_page_url.return_value = None

    # Initialize the PaginatedGitHubResource object
    paginator = PaginatedGitHubResource(lambda token, **params: fetch("url", token, **params), "token", 2)

    # Check that the iteration stops when there's no more data
    data = list(paginator)
    assert data == []
