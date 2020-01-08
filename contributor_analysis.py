import json
import requests
from pprint import pprint

github_base_url = 'https://api.github.com'


def get_stats_contributors(repo_url):
    """via GET /repos/:owner/:repo/stats/contributors"""
    stats_contributors_url = '{base_url}/repos/{repo_url}/stats/contributors'.format(
        base_url=github_base_url, repo_url=repo_url)
    contributors = requests.get(stats_contributors_url).json()

    stats_contributor_nr_commits = {}

    for contributor in contributors:
        contributor_name = contributor['author']['login']
        no_contributor_commits = contributor['total']
        stats_contributor_nr_commits[contributor_name] = no_contributor_commits

    print('stats_contributors:', len(stats_contributor_nr_commits))
    pprint(stats_contributor_nr_commits)


def get_contributors(repo_url):
    """via GET /repos/:owner/:repo/contributors"""

    contributors_url = '{base_url}/repos/{repo_url}/contributors'.format(
        base_url=github_base_url, repo_url=repo_url)
    contributors = requests.get(contributors_url).json()

    contributor_nr_commits = {}
    for contributor in contributors:
        contributor_name = contributor['login']
        no_contributor_commits = contributor['contributions']
        contributor_nr_commits[contributor_name] = no_contributor_commits

    print('contributors:', len(contributor_nr_commits))
    pprint(contributor_nr_commits)


def main():

    with open('repos.json') as repos_json:
        data = json.load(repos_json)

        for repo_url in data.values():
            print('repository:', repo_url)

            get_contributors(repo_url)

            get_stats_contributors(repo_url)


if __name__ == '__main__':
    main()
