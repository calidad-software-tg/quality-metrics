from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG")
REPO_NAME = os.getenv("REPO_NAME")

GITHUB_API_BASE = "https://api.github.com"
REPO_LOCAL_PATH = os.path.join(os.path.dirname(__file__), "..", "tldr")

if not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN no está definido en .env")