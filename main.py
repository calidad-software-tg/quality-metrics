from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from core.github_extractor import GitHubExtractor

from metrics.producto.churn import Churn
from metrics.producto.repo_stats import RepoStats
from metrics.proceso.commit_frequency import CommitFrequency
from metrics.proceso.commit_entropy import CommitEntropy
from metrics.proceso.continuous_integration import ContinuousIntegration
from metrics.proceso.forks_issues_prs import ForksIssuesPRs
from metrics.proceso.open_pull_requests import OpenPullRequests
from metrics.persona.developer_contribution import DeveloperContribution
from metrics.persona.developer_ownership import DeveloperOwnership
from metrics.persona.core_devs_prs import CoreDevsPRs
from metrics.persona.core_devs_rejected_prs import CoreDevsRejectedPRs

CORE_DEVELOPERS = []  # completar con los logins de GitHub de los devs principales

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)

metricas = [
    ("Churn",                     Churn(extractor)),
    ("CommitFrequency",           CommitFrequency(extractor)),
    ("CommitEntropy",             CommitEntropy(extractor)),
    ("ContinuousIntegration",     ContinuousIntegration(extractor)),
    ("DeveloperContribution",     DeveloperContribution(extractor)),
    ("DeveloperOwnership",        DeveloperOwnership(extractor)),
    ("RepoStats",                 RepoStats(extractor)),
    ("ForksIssuesPRs",            ForksIssuesPRs(extractor)),
    ("OpenPullRequests",          OpenPullRequests(extractor)),
    ("CoreDevsPRs",               CoreDevsPRs(extractor, CORE_DEVELOPERS)),
    ("CoreDevsRejectedPRs",       CoreDevsRejectedPRs(extractor, CORE_DEVELOPERS)),
]

for nombre, metrica in metricas:
    print(f"\n--- {nombre} ---")
    try:
        resultado = metrica.calcular(GITHUB_ORG, REPO_NAME, 5)
        print(resultado)
    except Exception as e:
        print(f"Error: {e}")