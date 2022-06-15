import json
import logging
import os
import pprint
import sys

from github import Github

LOGLEVEL = os.environ.get("LOGLEVEL", "WARNING").upper()
logging.basicConfig(level=LOGLEVEL)

if os.environ.get("GITHUB_TOKEN") is not None:
    _TOKEN = os.environ["GITHUB_TOKEN"]
else:
    logging.error("'GITHUB_TOKEN' environment variable was not set")
    sys.exit("Must set 'GITHUB_TOKEN' environment variable")

gh = Github(_TOKEN)

orgs = ["singlestone"]
orgs = ["ReverbTraining"]
# orgs = ["singlestone"], "ReverbTraining"]


def list_org_repos(org):
    logging.info(f"Listing repos for org: {org}")
    repo_list = []
    org = gh.get_organization(org)
    repos = org.get_repos()
    for repo in repos:
        repo_list.append(repo)
    return repo_list


def list_repo_admins(repo):
    logging.info(f"Listing admins for repo: {repo.name}")
    admin_list = []
    collabs = repo.get_collaborators()
    for collab in collabs:
        if collab.permissions.admin:
            admin_list.append(collab)
    return admin_list


def list_repo_maintainers(repo):
    logging.info(f"Listing maintainers for repo: {repo.name}")
    maintainer_list = []
    collabs = repo.get_collaborators()
    for collab in collabs:
        if collab.permissions.maintain:
            maintainer_list.append(collab)
    return maintainer_list


def print_results(results, indent=2):
    pp = pprint.PrettyPrinter(indent=indent)
    pp.pprint(results)


def export_results_json(results):
    logging.info("Exporting results to github_org_repo_access.json")
    with open("github_org_repo_access.json", "w") as f:
        json.dump(results, f, indent=2)


# Main program
results = []
for org in orgs:
    logging.info(f"Reviewing repos for org: {org}")
    repos = list_org_repos(org)
    logging.info(f"There are {len(repos)} repos")
    for repo in repos:
        logging.info(f"Reviewing repo: {repo.name}")
        repo_admins = list_repo_admins(repo)
        logging.info(f"There are {len(repo_admins)} admins")

        admin_results = []
        for repo_admin in repo_admins:
            admin_result = {
                "name": repo_admin.name,
                "login": repo_admin.login,
                "email": repo_admin.email,
            }
            admin_results.append(admin_result)
        result = {
            "name": repo.name,
            "org": repo.organization.login,
            "admins": admin_results,
        }
        logging.info(f"Adding result: {result}")
        results.append(result)


print_results(results)
export_results_json(results)
