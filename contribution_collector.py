import json
import requests

from util import util


def get(url: str):
    """
    making GET requests adding authorization header
    :returns the full response from `requests.get()`
    """
    response = requests.get(url=url, headers={'Authorization': 'token %s' % util.api_token})
    print('Getting %s, response code: %i' % (url, response.status_code))
    if not response:
        print('Failed request: %s' % response)

    return response


def get_stats_contributors(repo_owner: str, repo_name: str) -> {str: int}:
    """
    via GET /repos/:owner/:repo/stats/contributors
    :returns a dictionary with key: user_name and value: number of commits to repo
    """
    stats_contributors_url = '{base_url}/repos/{repo_owner}/{repo_name}/stats/contributors'.format(
        base_url=util.github_v3_api_base_url, repo_owner=repo_owner, repo_name=repo_name)

    # the top 100 contributors to the repo
    contributors = get(stats_contributors_url).json()
    repo_contributor_contributions = {}
    for contributor in contributors:
        contributor_name = contributor['author']['login']
        repo_contributor_contributions[contributor_name] = contributor['total']
    return repo_contributor_contributions


def collect_contribution_data(oss_repos_file_path: str) -> {}:
    with open(oss_repos_file_path) as repos_json:
        data = json.load(repos_json)

        project_contributors = {}

        # for each of the selected projects (in oss_repos.json)
        for project in data.values():
            repo_owner = project['owner']     # e.g. 'flutter'
            repo_name = project['repo_name']  # e.g. 'flutter'
            domain = project['domain']        # e.g. 'dart' -> the actual language used in other projects
            company = project['company']      # e.g. 'google'

            print('repository:', '{}/{}'.format(repo_owner, repo_name))

            # get top 100 contributors of domain repo and the number of their commits to it
            stats_contributor_nr_commits = get_stats_contributors(repo_owner=repo_owner, repo_name=repo_name)
            project_contributors[domain] = dict(
                repo_owner=repo_owner, repo_name=repo_name, domain=domain, company=company,
                contributors=stats_contributor_nr_commits
            )

        util.cache_contributor_stats_to_json(project_contributor_contributions=project_contributors)
        return project_contributors
