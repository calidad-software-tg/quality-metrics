import json
import os
from git import Repo


class GitExtractor:
    def __init__(self, repo_path: str, cache_dir: str = None):
        self._repo = Repo(os.path.abspath(repo_path))
        self._cache_dir = cache_dir

    def iter_commits(self, limite: int = None, since_sha: str = None):
        """Yields commits from HEAD. Stops at since_sha (exclusive) or after limite commits."""
        for i, commit in enumerate(self._repo.iter_commits("HEAD")):
            if limite and i >= limite:
                break
            if since_sha and commit.hexsha == since_sha:
                break
            yield commit

    def head_sha(self) -> str:
        return self._repo.head.commit.hexsha

    def repo_path(self) -> str:
        return self._repo.working_dir

    def load_cache(self, key: str) -> dict | None:
        if not self._cache_dir:
            return None
        path = os.path.join(self._cache_dir, f"cache_{key}.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None

    def save_cache(self, key: str, data: dict):
        if not self._cache_dir:
            return
        os.makedirs(self._cache_dir, exist_ok=True)
        path = os.path.join(self._cache_dir, f"cache_{key}.json")
        with open(path, "w") as f:
            json.dump(data, f)
