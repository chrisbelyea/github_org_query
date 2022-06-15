# GitHub Organization Query

Scans specified GitHub organizations and returns a list of all repositories and their administrators.

## Requirements

- Python 3
- Use a virtualenv
- Install dependencies (`pip install -r requirements.txt`)
- Set up a GitHub API token and export it to a `GITHUB_TOKEN` environment variable
- The API token needs approximately the following permissions (probably less):
  - `repo`
  - `read:discussion`
  - `read:enterprise`
  - `read:gpg_key`
  - `read:org`
  - `read:public_key`
  - `read:repo_hook`
  - `read:user`
  - `user:email`

## Usage

```shell
$ python ghoq.py --help
```

```shell
usage: ghoq.py [-h] [--quiet] [--json] [--csv] org [org ...]

List GitHub organization repos and their admins.

positional arguments:
  org         List of GitHub Organizations to analyze

options:
  -h, --help  show this help message and exit
  --quiet     Do not print results to stdout
  --json      Export results to github_org_repo_access.json
  --csv       Export results to github_org_repo_access.csv
```

For example,

```shell
$ python ghoq.py myorg1 myorg2 --quiet --json --csv
```

Will scan GitHub organizations "myorg1" and "myorg2", export the results to both JSON and CSV files, and suppress the output from stdout.
