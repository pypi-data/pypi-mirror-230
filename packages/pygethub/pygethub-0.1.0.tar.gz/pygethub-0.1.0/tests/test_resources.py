import pytest
import time
from unittest.mock import Mock, patch
from requests.models import Response
from requests.exceptions import HTTPError
from pygethub.resources import (
    calculate_delay,
    fetch,
    list_github_resource,
    list_commits,
    list_branches,
    list_users,
    list_organizations,
    list_org_repos,
    list_user_repos,
    list_contributors,
    check_rate_limit
)

def test_calculate_delay():
    # Create a mock response with specific 'X-RateLimit-Remaining' and 'X-RateLimit-Reset' headers
    response = Mock(headers={'X-RateLimit-Remaining': '50', 'X-RateLimit-Reset': '1629459260'})
    
    # Mock time.time to return a specific current time
    with patch('time.time', return_value=1629459200):
        # Call the function with the mock response
        delay = calculate_delay(response)

    # Check that the delay is calculated correctly
    assert delay == 1.2

def test_calculate_delay_no_remaining():
    # Create a mock response with 'X-RateLimit-Remaining' header set to '0'
    response = Mock(headers={'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1629459260'})
    
    # Mock time.time to return a specific current time
    with patch('time.time', return_value=1629459200):
        # Call the function with the mock response
        delay = calculate_delay(response)

    # Check that the delay is equal to the window
    assert delay == 60

def test_calculate_delay_reset_in_past():
    # Create a mock response with 'X-RateLimit-Remaining' header set to '0' and 'X-RateLimit-Reset' header set to a time in the past
    response = Mock(headers={'X-RateLimit-Remaining': '0', 'X-RateLimit-Reset': '1629459140'})
    
    # Mock time.time to return a specific current time
    with patch('time.time', return_value=1629459200):
        # Call the function with the mock response
        delay = calculate_delay(response)

    # Check that the delay is equal to 1
    assert delay == 1

@patch('requests.Session.get', autospec=True)
def test_fetch_success(mock_get):
    # Create a mock response
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"key": "value"}
    mock_response.headers = {"X-RateLimit-Remaining": "100", "X-RateLimit-Reset": str(int(time.time() + 100))}

    # Configure the mock get to return the mock response
    mock_get.return_value = mock_response

    # Call the function with the mock response
    result = fetch('https://api.github.com/users', 'token')
    
    # Assert the function returned the expected result
    assert result == {"success": True, "data": {"key": "value"}, "link": None}


@patch('requests.Session.get', autospec=True)
def test_fetch_http_error(mock_get):
    # Configure the mock get to raise an HTTPError
    mock_get.side_effect = HTTPError('HTTP Error occurred')

    # Call the function
    result = fetch('https://api.github.com/users', 'token')

    # Assert the function returned the expected result
    assert result == {"success": False, "message": 'HTTP Error occurred'}


@patch('requests.Session.get', autospec=True)
def test_fetch_unexpected_error(mock_get):
    # Configure the mock get to raise an Exception
    mock_get.side_effect = Exception('Unexpected error')

    # Call the function
    result = fetch('https://api.github.com/users', 'token')

    # Assert the function returned the expected result
    assert result == {"success": False, "message": 'Unexpected error'}


@patch('requests.Session.get', autospec=True)
@patch('time.sleep', side_effect=lambda x: None)  # Mock sleep to avoid actual delay
def test_fetch_respects_rate_limit(mock_sleep, mock_get):
    # Create a mock response
    mock_response = Mock(spec=Response)
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"key": "value"}
    mock_response.headers = {"X-RateLimit-Remaining": "1", "X-RateLimit-Reset": str(int(time.time() + 1))}

    # Configure the mock get to return the mock response
    mock_get.return_value = mock_response

    # Call the function with the mock response
    fetch('https://api.github.com/users', 'token')

    # Assert sleep was called with the correct delay
    mock_sleep.assert_called_once_with(1)

def test_list_github_resource():
    # Mock the fetch function
    with patch('pygethub.resources.fetch', autospec=True) as mock_fetch:
        # Configure the mock to return a specific dictionary
        mock_fetch.return_value = {"success": True, "data": "data", "link": None}

        # Call the function with a specific resource path and token
        result = list_github_resource('/users', 'token')

        # Assert the function called fetch with the correct URL and token
        mock_fetch.assert_called_once_with('https://api.github.com/users', 'token')

        # Assert the function returned the result from fetch
        assert result == {"success": True, "data": "data", "link": None}

def test_list_github_resource_with_additional_arguments():
    # Mock the fetch function
    with patch('pygethub.resources.fetch', autospec=True) as mock_fetch:
        # Configure the mock to return a specific dictionary
        mock_fetch.return_value = {"success": True, "data": "data", "link": None}

        # Call the function with a specific resource path, token, and extra arguments
        result = list_github_resource('/users', 'token', param1='value1', param2='value2')

        # Assert the function called fetch with the correct URL, token, and extra arguments
        mock_fetch.assert_called_once_with('https://api.github.com/users', 'token', param1='value1', param2='value2')

        # Assert the function returned the result from fetch
        assert result == {"success": True, "data": "data", "link": None}

def test_list_commits():
    owner = 'test_owner'
    repo = 'test_repo'
    token = 'test_token'
    additional_arg = 'test_arg'
    
    # Mock the list_github_resource function
    with patch('pygethub.resources.list_github_resource', autospec=True) as mock_list_github_resource:
        # Configure the mock to return a specific value
        mock_list_github_resource.return_value = 'test_return_value'

        # Call the function
        result = list_commits(owner, repo, token, additional_arg=additional_arg)

        # Check that list_github_resource was called with the correct arguments
        mock_list_github_resource.assert_called_once_with(f"/repos/{owner}/{repo}/commits", token, additional_arg=additional_arg)
        
        # Check that the return value is correct
        assert result == 'test_return_value'

def test_list_branches():
    owner = 'test_owner'
    repo = 'test_repo'
    token = 'test_token'
    additional_arg = 'test_arg'
    
    # Mock the list_github_resource function
    with patch('pygethub.resources.list_github_resource', autospec=True) as mock_list_github_resource:
        # Configure the mock to return a specific value
        mock_list_github_resource.return_value = 'test_return_value'

        # Call the function
        result = list_branches(owner, repo, token, additional_arg=additional_arg)

        # Check that list_github_resource was called with the correct arguments
        mock_list_github_resource.assert_called_once_with(f"/repos/{owner}/{repo}/branches", token, additional_arg=additional_arg)
        
        # Check that the return value is correct
        assert result == 'test_return_value'

def test_list_users():
    token = 'test_token'
    since = 123
    additional_arg = 'test_arg'
    
    # Mock the list_github_resource function
    with patch('pygethub.resources.list_github_resource', autospec=True) as mock_list_github_resource:
        # Configure the mock to return a specific value
        mock_list_github_resource.return_value = 'test_return_value'

        # Call the function
        result = list_users(token, since=since, additional_arg=additional_arg)

        # Check that list_github_resource was called with the correct arguments
        mock_list_github_resource.assert_called_once_with("/users", token, since=since, additional_arg=additional_arg)
        
        # Check that the return value is correct
        assert result == 'test_return_value'

def test_list_organizations():
    token = 'test_token'
    since = 123
    additional_arg = 'test_arg'
    
    # Mock the list_github_resource function
    with patch('pygethub.resources.list_github_resource', autospec=True) as mock_list_github_resource:
        # Configure the mock to return a specific value
        mock_list_github_resource.return_value = 'test_return_value'

        # Call the function
        result = list_organizations(token, since=since, additional_arg=additional_arg)

        # Check that list_github_resource was called with the correct arguments
        mock_list_github_resource.assert_called_once_with("/organizations", token, since=since, additional_arg=additional_arg)
        
        # Check that the return value is correct
        assert result == 'test_return_value'

def test_list_org_repos():
    org_name = 'test_org'
    token = 'test_token'
    additional_arg = 'test_arg'
    
    # Mock the list_github_resource function
    with patch('pygethub.resources.list_github_resource', autospec=True) as mock_list_github_resource:
        # Configure the mock to return a specific value
        mock_list_github_resource.return_value = 'test_return_value'

        # Call the function
        result = list_org_repos(org_name, token, additional_arg=additional_arg)

        # Check that list_github_resource was called with the correct arguments
        mock_list_github_resource.assert_called_once_with(f"/orgs/{org_name}/repos", token, additional_arg=additional_arg)
        
        # Check that the return value is correct
        assert result == 'test_return_value'

def test_list_user_repos():
    username = 'test_user'
    token = 'test_token'
    additional_arg = 'test_arg'
    
    # Mock the list_github_resource function
    with patch('pygethub.resources.list_github_resource', autospec=True) as mock_list_github_resource:
        # Configure the mock to return a specific value
        mock_list_github_resource.return_value = 'test_return_value'

        # Call the function
        result = list_user_repos(username, token, additional_arg=additional_arg)

        # Check that list_github_resource was called with the correct arguments
        mock_list_github_resource.assert_called_once_with(f"/users/{username}/repos", token, additional_arg=additional_arg)
        
        # Check that the return value is correct
        assert result == 'test_return_value'

def test_list_contributors():
    owner = 'test_owner'
    repo = 'test_repo'
    token = 'test_token'
    additional_arg = 'test_arg'
    
    # Mock the list_github_resource function
    with patch('pygethub.resources.list_github_resource', autospec=True) as mock_list_github_resource:
        # Configure the mock to return a specific value
        mock_list_github_resource.return_value = 'test_return_value'

        # Call the function
        result = list_contributors(owner, repo, token, additional_arg=additional_arg)

        # Check that list_github_resource was called with the correct arguments
        mock_list_github_resource.assert_called_once_with(f"/repos/{owner}/{repo}/contributors", token, additional_arg=additional_arg)
        
        # Check that the return value is correct
        assert result == 'test_return_value'

def test_check_rate_limit():
    token = 'test_token'
    additional_arg = 'test_arg'
    
    # Mock the list_github_resource function
    with patch('pygethub.resources.list_github_resource', autospec=True) as mock_list_github_resource:
        # Configure the mock to return a specific value
        mock_list_github_resource.return_value = 'test_return_value'

        # Call the function
        result = check_rate_limit(token, additional_arg=additional_arg)

        # Check that list_github_resource was called with the correct arguments
        mock_list_github_resource.assert_called_once_with("/rate_limit", token, additional_arg=additional_arg)
        
        # Check that the return value is correct
        assert result == 'test_return_value'
