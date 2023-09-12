# pygethub
[![Build](https://github.com/chrisammon3000/pygethub/actions/workflows/run_tests.yml/badge.svg?style=for-the-badge)](https://github.com/chrisammon3000/pygethub/actions/workflows/run_tests.yml) [![codecov](https://codecov.io/github/chrisammon3000/pygethub/branch/main/graph/badge.svg?token=QSZLP51RWJ)](https://codecov.io/github/chrisammon3000/pygethub?style=for-the-badge) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

`pygethub` is a simple Python library for working with the GitHub API. It provides easy-to-use functions for common tasks and supports pagination through the API responses.

## Features

- Get a list of commits for a specific repository.
- Get a list of branches for a specific repository.
- List GitHub users and organizations.
- List repositories for a specific organization or user.
- Get a list of contributors for a specific repository.
- Check the rate limit for the authenticated user.
- Start and resume pagination of global resources.

## Installation

To install `pygethub`, you can use pip:

```
pip install pygethub
```

## Usage

Here is an example of how you can use `pygethub`:

<!-- TODO Add example of using paginator with params, see gfe-db notebook for GitHub EDA list_branches -->
```python
from pygethub import list_commits, GitHubPaginator, list_users

# List commits for a specific repository
commits = list_commits('owner', 'repo', 'your-github-token')
print(commits)

# Use pagination to list users
paginator = GitHubPaginator('your-github-token')

# List users from the beginning, include other request parameters as keyword arguments
users = paginator.get_paginator(list_users)
for user in users:
    print(user)

# If you want to resume the listing from a certain user ID, use the `since` parameter
users = paginator.get_paginator(list_users, since=500)
for user in users:
    print(user)

# Similarly, you can use the `since` parameter with list_organizations to resume listing from a certain organization ID
```

## Development

To install `pygethub`, along with the tools you need to develop and run tests, run the following in your virtual environment:

```
pip install -e .[dev,test]
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) on how to contribute to `pygethub`.

## License

`pygethub` is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for the full license text.