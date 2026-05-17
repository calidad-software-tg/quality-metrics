from core.base import Metrica

class Churn(Metrica):
    nombre = "Churn"

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        commits = self._extractor.get_commits(owner, repo, limite=limite)
        max_added = max_deleted = max_changed = 0

        for commit in commits:
            for file in self._extractor.get_commit_files(commit["url"]):
                added = file.get("additions", 0)
                deleted = file.get("deletions", 0)
                max_added = max(max_added, added)
                max_deleted = max(max_deleted, deleted)
                max_changed = max(max_changed, added + deleted)

        return {
            "max_lines_added": max_added,
            "max_lines_deleted": max_deleted,
            "max_lines_changed": max_changed,
        }