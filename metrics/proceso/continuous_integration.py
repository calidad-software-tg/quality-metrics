from core.base import Metrica

CI_FILES = {".travis.yml", ".gitlab-ci.yml", "Jenkinsfile", ".circleci", ".github"}


class ContinuousIntegration(Metrica):
    nombre = "Integración Continua"
    descripcion = (
        "Verifica si el repositorio contiene archivos de configuración de CI "
        "(Travis CI, GitHub Actions, GitLab CI, CircleCI, Jenkins)."
    )
    dimension = ["Proceso"]
    interpretacion = (
        "La presencia de CI es un indicador positivo de madurez en el proceso de desarrollo: "
        "automatiza pruebas, compilaciones y despliegues, reduciendo errores manuales."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        contents = self._extractor.get_repo_contents(owner, repo)
        names = {item["name"] for item in contents}
        found = sorted(CI_FILES & names)
        return {
            "has_ci": bool(found),
            "ci_files_found": found,
        }