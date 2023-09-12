import time
import requests

session = requests.Session()

# Headers
session.headers = {
    "Authorization": "",
    "Content-Type": "application/json",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

def calculate_delay(response):
    """Calculate delay based on X-RateLimit-Remaining and X-RateLimit-Reset headers."""
    remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(response.headers.get('X-RateLimit-Reset', 0))  # UTC epoch seconds
    current_time = time.time()  # UTC epoch seconds

    # Calculate the time window until the rate limit resets
    window = max(reset_time - current_time, 1)

    # Calculate the delay to ensure we don't exceed the rate limit
    if remaining > 0:
        delay = window / remaining
    else:
        delay = window

    return delay

def fetch(url: str, token: str, **params) -> dict:
    session.headers["Authorization"] = f"token {token}"

    # Update the user-agent if provided in the params
    if "user_agent" in params:
        session.headers["User-Agent"] = params["user_agent"]
        del params["user_agent"]

    try:
        response = session.get(url, params=params)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        # Add additional error information
        return {"success": False, "message": str(http_err)}
    except Exception as err:
        # Handle unexpected exceptions
        return {"success": False, "message": str(err)}
    
    # Respect rate limit by adding a delay between requests
    delay = calculate_delay(response)
    time.sleep(delay)
    
    # Return data along with link header for pagination
    return {"success": True, "data": response.json(), "link": response.headers.get('Link')}


def list_github_resource(resource_path: str, token: str, **kwargs) -> dict:
    """Return a list of GitHub resources based on the provided resource path"""
    base_url = "https://api.github.com"
    url = base_url + resource_path

    return fetch(url, token, **kwargs)

# Wrapper functions for better readability and resource path consistency
def list_commits(owner: str, repo: str, token: str, **kwargs) -> dict:
    """Return a list of GitHub commits for the specified repository"""
    resource_path = f"/repos/{owner}/{repo}/commits"
    return list_github_resource(resource_path, token, **kwargs)

def list_branches(owner: str, repo: str, token: str, **kwargs) -> dict:
    """Return a list of GitHub branches for the specified repository"""
    resource_path = f"/repos/{owner}/{repo}/branches"
    return list_github_resource(resource_path, token, **kwargs)

def list_users(token: str, since=None, **kwargs) -> dict:
    """Return a list of GitHub users"""
    resource_path = "/users"
    return list_github_resource(resource_path, token, since=since, **kwargs)

def list_organizations(token: str, since=None, **kwargs) -> dict:
    """Return a list of GitHub organizations"""
    resource_path = "/organizations"
    return list_github_resource(resource_path, token, since=since, **kwargs)

def list_org_repos(org_name: str, token: str, **kwargs) -> dict:
    """Return a list of GitHub repos for the specified organization"""
    resource_path = f"/orgs/{org_name}/repos"
    return list_github_resource(resource_path, token, **kwargs)

def list_user_repos(username: str, token: str, **kwargs) -> dict:
    """Return a list of GitHub repos for the specified user"""
    resource_path = f"/users/{username}/repos"
    return list_github_resource(resource_path, token, **kwargs)

def list_contributors(owner: str, repo: str, token: str, **kwargs) -> dict:
    """Return a list of contributors for the specified repository"""
    resource_path = f"/repos/{owner}/{repo}/contributors"
    return list_github_resource(resource_path, token, **kwargs)

def check_rate_limit(token: str, **kwargs) -> dict:
    """Return the rate limit information for the authenticated user"""
    resource_path = "/rate_limit"
    return list_github_resource(resource_path, token, **kwargs)
