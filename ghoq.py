import argparse
import csv
import json
import logging
import os
import sys

from github import Github
from tqdm import tqdm

LOGLEVEL = os.environ.get("LOGLEVEL", "CRITICAL").upper()
logging.basicConfig(level=LOGLEVEL)

# Check that GitHub API token is set as an environment variable
if os.environ.get("GITHUB_TOKEN") is not None:
    _TOKEN = os.environ["GITHUB_TOKEN"]
else:
    logging.error("'GITHUB_TOKEN' environment variable was not set")
    sys.exit("Must set 'GITHUB_TOKEN' environment variable")

# Set up GitHub API client
gh = Github(_TOKEN)


def list_org_repos(org):
    """List repositories that belong to an organization"""
    logging.info(f"Listing repos for org: {org}")
    repo_list = []
    org = gh.get_organization(org)
    repos = org.get_repos()
    for repo in repos:
        repo_list.append(repo)
    return repo_list


def list_repo_admins(repo):
    """List administrator(s) for a repository"""
    logging.info(f"Listing admins for repo: {repo.name}")
    admin_list = []
    collabs = repo.get_collaborators()
    for collab in collabs:
        if collab.permissions.admin:
            admin_list.append(collab)
    return admin_list


def list_repo_maintainers(repo):
    """List maintainer(s) for a repository"""
    logging.info(f"Listing maintainers for repo: {repo.name}")
    maintainer_list = []
    collabs = repo.get_collaborators()
    for collab in collabs:
        if collab.permissions.maintain:
            maintainer_list.append(collab)
    return maintainer_list


def print_results(results, indent=2):
    """Print results in JSON format to stdout"""
    print(json.dumps(results, indent=2))


def export_results_json(results):
    """Export results to a JSON file"""
    logging.info("Exporting results to github_org_repo_access.json")
    with open("github_org_repo_access.json", "w") as f:
        json.dump(results, f, indent=2)


def export_results_csv(results):
    """Export results to a CSV file"""
    logging.info("Exporting results to github_org_repo_access.csv")

    def convert_admins_dict_to_string(result):
        admins = []
        for admin in result["admins"]:
            logging.info(f"admin: {admin}")
            admins.append(admin["login"])
        admins_str = ";".join(admins)
        return admins_str

    with open("github_org_repo_access.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(["repo", "org", "admins", "private"])
        for result in results:
            logging.info(f"result: {result}")
            result["admins"] = convert_admins_dict_to_string(result)
            writer.writerow(result.values())


if __name__ == "__main__":
    """Main program entrypoint when run directly."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="List GitHub organization repos and their admins."
    )
    parser.add_argument(
        "organizations",
        metavar="org",
        type=str,
        nargs="+",
        help="List of GitHub Organizations to analyze",
    )
    parser.add_argument(
        "--quiet",
        help="Do not print results to stdout",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--json",
        help="Export results to github_org_repo_access.json",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--csv",
        help="Export results to github_org_repo_access.csv",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    orgs = args.organizations

    results = []
    with tqdm(orgs, desc="analyzing organizations", unit="org") as orgs_progress:
        for org in orgs_progress:
            orgs_progress.set_description(desc=f"Analyzing org: {org}", refresh=True)
            logging.info(f"Reviewing repos for org: {org}")
            repos = list_org_repos(org)
            logging.info(f"There are {len(repos)} repos")
            with tqdm(repos, desc="analyzing repos", unit="repo") as repos_progress:
                for repo in repos_progress:
                    repos_progress.set_description(desc=f"Analyzing {org}/{repo.name}")
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
                        "private": repo.private,
                    }
                    logging.info(f"Adding result: {result}")
                    results.append(result)
                repos_progress.close()

    if not args.quiet:
        print_results(results)
    if args.json:
        export_results_json(results)
    if args.csv:
        export_results_csv(results)
