from .resources import fetch

def get_next_page_url(link_header):
    """Extract next page URL from link header"""
    if link_header is None:
        return None

    links = link_header.split(", ")
    for link in links:
        url, rel = link.split("; ")
        if "rel=\"next\"" in rel:
            return url.strip("<>")
    return None

class PaginatedGitHubResource:
    def __init__(self, list_function, token, per_page, since=None, **kwargs):
        self.list_function = list_function
        self.per_page = per_page
        self.token = token
        self.since = since
        self.kwargs = kwargs
        self.data = []
        self.next_page_url = None
        self.page_counter = 0  # Create a page counter to count the pages.

    def __iter__(self):
        while True:
            if not self.data:
                if self.next_page_url:
                    # If we have a next page URL, we use it directly
                    response = self.list_function(token=self.token, **self.kwargs)
                else:
                    # If we don't have a next page URL, we fetch the first page
                    response = self.list_function(token=self.token, per_page=self.per_page, since=self.since, **self.kwargs)
                
                self.data = response.get("data", [])
                
                if not self.data:
                    break

                self.page_counter += 1  # Increment the page counter
                print(f"Page {self.page_counter}: {len(self.data)} items")

                # Get next page URL from link header
                self.next_page_url = get_next_page_url(response.get('link', ''))
                if self.next_page_url:
                    self.list_function = lambda token, **params: fetch(self.next_page_url, token, **params)
                else:
                    while self.data:
                        yield self.data.pop(0)

                    break # No more pages to fetch

            yield self.data.pop(0)

class GitHubPaginator:
    def __init__(self, token, per_page=100):
        self.token = token
        self.per_page = per_page

    def get_paginator(self, list_function, **kwargs):
        return PaginatedGitHubResource(list_function, self.token, self.per_page, **kwargs)