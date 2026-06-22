import os

from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME, REPO_LOCAL_PATH  # noqa: F401
from core.github_extractor import GitHubExtractor
from core.git_extractor import GitExtractor

# from metrics.producto.churn import Churn  # noqa: F401
# from metrics.restantes.repo_stats import RepoStats  # noqa: F401
# from metrics.commit_frequency.commit_frequency import CommitFrequency  # noqa: F401
# from metrics.proceso.commit_entropy import CommitEntropy  # noqa: F401
# from metrics.restantes.continuous_integration import ContinuousIntegration  # noqa: F401
# from metrics.restantes.forks_issues_prs import ForksIssuesPRs  # noqa: F401
# from metrics.restantes.open_pull_requests import OpenPullRequests  # noqa: F401
# from metrics.persona.developer_contribution import DeveloperContribution  # noqa: F401
from metrics.restantes.developer_ownership import DeveloperOwnership  # noqa: F401
# from metrics.restantes.core_devs_prs import CoreDevsPRs  # noqa: F401
# from metrics.persona.core_devs_rejected_prs import CoreDevsRejectedPRs  # noqa: F401
from metrics.social_interaction.social_interaction import SocialInteractionBetweenDevelopers  # noqa: F401
from metrics.number_of_open_issues.number_of_open_issues import NumberOfOpenIssues  # noqa: F401
from metrics.defect_recurrence_rate.defect_recurrence_rate import DefectRecurrenceRate  # noqa: F401
from metrics.development_velocity.development_velocity import DevelopmentVelocity  # noqa: F401
from metrics.user_reported_bugs.user_reported_bugs import UserReportedBugs  # noqa: F401
from metrics.active_branches.active_branches import NumberOfActiveBranches  # noqa: F401



CORE_DEVELOPERS = []  # completar con los logins de GitHub de los devs principales

cache_dir = os.path.join(os.path.dirname(__file__), "data", "raw")
git = GitExtractor(REPO_LOCAL_PATH, cache_dir=cache_dir)
gh = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)

ORIGINAL_OWNER = "tldr-pages"
ORIGINAL_REPO  = "tldr"

# Cada tupla: (nombre, metrica, owner, repo)
# Las métricas de comunidad usan el repo original; el resto usa el fork propio.
metricas = [
    # local git — rápidas, sin rate limit
    # ("Churn",                  Churn(git),                        GITHUB_ORG,     REPO_NAME),
    # ("CommitFrequency",        CommitFrequency(git),              GITHUB_ORG,     REPO_NAME),
    # ("CommitEntropy",          CommitEntropy(git),                GITHUB_ORG,     REPO_NAME),
    # ("DeveloperContribution",  DeveloperContribution(git),        GITHUB_ORG,     REPO_NAME),
    # GitHub API — repo propio
    # ("ContinuousIntegration",  ContinuousIntegration(gh),         GITHUB_ORG,     REPO_NAME),
    # ("RepoStats",              RepoStats(gh),                     GITHUB_ORG,     REPO_NAME),
    # ("DeveloperOwnership",     DeveloperOwnership(gh),           GITHUB_ORG,     REPO_NAME),
    # ("CoreDevsPRs",            CoreDevsPRs(gh, CORE_DEVELOPERS),  GITHUB_ORG,     REPO_NAME),
    # ("CoreDevsRejectedPRs",    CoreDevsRejectedPRs(gh, CORE_DEVELOPERS), GITHUB_ORG, REPO_NAME),
    # GitHub API — repo original (forks, issues, PRs reales)
    # ("ForksIssuesPRs",         ForksIssuesPRs(gh),                ORIGINAL_OWNER, ORIGINAL_REPO),
    # ("OpenPullRequests",       OpenPullRequests(gh),              ORIGINAL_OWNER, ORIGINAL_REPO),
    # ("SocialInteraction", SocialInteractionBetweenDevelopers(gh), ORIGINAL_OWNER, ORIGINAL_REPO),
    # ("NumberOfOpenIssues", NumberOfOpenIssues(gh), ORIGINAL_OWNER, ORIGINAL_REPO),
    # ("DefectRecurrenceRate", DefectRecurrenceRate(gh), ORIGINAL_OWNER, ORIGINAL_REPO),
    # ("DevelopmentVelocity", DevelopmentVelocity(gh), ORIGINAL_OWNER, ORIGINAL_REPO),
    # ("UserReportedBugs", UserReportedBugs(gh), ORIGINAL_OWNER, ORIGINAL_REPO), todo: validar core_developers y depues pasarselo al metodo
    # ("NumberOfActiveBranches", NumberOfActiveBranches(gh), ORIGINAL_OWNER, ORIGINAL_REPO),
]

for nombre, metrica, owner, repo in metricas:
    print(f"\n--- {nombre} ---")
    try:
        resultado = metrica.calcular(owner, repo)
        print(resultado)
    except Exception as e:
        print(f"Error: {e}")

