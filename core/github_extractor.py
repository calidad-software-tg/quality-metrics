import requests

GRAPHQL_URL = "https://api.github.com/graphql"

class GitHubExtractor:
    def __init__(self, token, api_base):
        self._token = token
        self._api_base = api_base
        self._headers = {"Authorization": f"token {self._token}"}
        self._graphql_headers = {"Authorization": f"bearer {self._token}"}

    def get_commits(self, owner: str, repo: str, limite: int = None) -> list:
        url = f"{self._api_base}/repos/{owner}/{repo}/commits"
        if limite:
            params = {"per_page": min(limite, 100)}
            return self._request(url, params).json()[:limite]
        return self._get_paginated(url)

    def get_commit_files(self, commit_url: str) -> list:
        return self._request(commit_url).json().get("files", [])

    def get_repo_contents(self, owner: str, repo: str, path: str = "") -> list:
        url = f"{self._api_base}/repos/{owner}/{repo}/contents/{path}"
        return self._request(url).json()

    def get_pull_requests(self, owner: str, repo: str, state: str = "all") -> list:
        url = f"{self._api_base}/repos/{owner}/{repo}/pulls"
        return self._get_paginated(url, {"state": state, "per_page": 100})

    def get_repo_tree(self, owner: str, repo: str, sha: str = "HEAD") -> list:
        url = f"{self._api_base}/repos/{owner}/{repo}/git/trees/{sha}"
        return self._request(url, {"recursive": "1"}).json().get("tree", [])

    def search_issues(self, query: str) -> dict:
        url = f"{self._api_base}/search/issues"
        return self._request(url, {"q": query}).json()

    def graphql(self, query: str, variables: dict = None) -> dict:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        response = requests.post(GRAPHQL_URL, json=payload, headers=self._graphql_headers)
        response.raise_for_status()
        return response.json()

    def _request(self, url: str, params: dict = None) -> requests.Response:
        response = requests.get(url, headers=self._headers, params=params)
        response.raise_for_status()
        return response

    def _get_paginated(self, url: str, params: dict = None) -> list:
        results = []
        while url:
            response = self._request(url, params)
            data = response.json()
            results.extend(data if isinstance(data, list) else [data])
            url = response.links.get("next", {}).get("url")
            params = None
        return results