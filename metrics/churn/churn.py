from core.base import Metrica


class Churn(Metrica):
    nombre = "Churn"
    descripcion = (
        "Mide el volumen máximo de líneas agregadas, eliminadas y modificadas "
        "en un archivo individual a lo largo de los commits del repositorio."
    )
    dimension = ["Producto"]
    interpretacion = (
        "Un churn alto puede indicar inestabilidad en el código o refactorizaciones frecuentes. "
        "Un churn bajo sostenido sugiere código estable y maduro."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str = None, repo: str = None, limite: int = None) -> dict:
        cache = self._extractor.load_cache("churn") if not limite else None
        last_sha = cache.get("last_sha") if cache else None
        max_added = cache.get("max_lines_added", 0) if cache else 0
        max_deleted = cache.get("max_lines_deleted", 0) if cache else 0
        max_changed = cache.get("max_lines_changed", 0) if cache else 0

        newest_sha = None
        for commit in self._extractor.iter_commits(limite=limite, since_sha=last_sha):
            if newest_sha is None:
                newest_sha = commit.hexsha
            for stats in commit.stats.files.values():
                added = stats.get("insertions", 0)
                deleted = stats.get("deletions", 0)
                max_added = max(max_added, added)
                max_deleted = max(max_deleted, deleted)
                max_changed = max(max_changed, added + deleted)

        if newest_sha and not limite:
            self._extractor.save_cache("churn", {
                "last_sha": newest_sha,
                "max_lines_added": max_added,
                "max_lines_deleted": max_deleted,
                "max_lines_changed": max_changed,
            })

        return {
            "max_lines_added": max_added,
            "max_lines_deleted": max_deleted,
            "max_lines_changed": max_changed,
        }