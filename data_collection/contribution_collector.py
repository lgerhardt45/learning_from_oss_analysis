import json

from data_collection.api.api import API


def get_stats_contributors(repo_owner: str, repo_name: str, api_client) -> {str: int}:
    """
    via GET /repos/:owner/:repo/stats/contributors
    :returns a dictionary with key: user_name and value: number of commits to repo
    """
    stats_contributors_url = 'repos/{repo_owner}/{repo_name}/stats/contributors'.format(
        repo_owner=repo_owner, repo_name=repo_name)

    # the top 100 contributors to the repo
    contributors = api_client.get_v3(stats_contributors_url).json()
    repo_contributor_contributions = {}
    for contributor in contributors:
        contributor_name: str = contributor['author']['login']
        # no bots and no users with only digits as user_name (the api doesn't like that)
        if not (contributor_name.endswith('[bot]') or contributor_name.isdigit()):
            repo_contributor_contributions[contributor_name] = contributor['total']
    return repo_contributor_contributions


def cache_contributor_stats_to_json(project_contributor_contributions: {}):
    import os
    cached_contributions_json_file_path: str = 'domain_contributors_contributions.json'
    if os.path.exists(cached_contributions_json_file_path):
        try:
            os.remove(cached_contributions_json_file_path)
            print('Removed "cached" contributor json file')
        except IOError:
            print('failed to remove old json file')
            return
    with open(cached_contributions_json_file_path, mode='a') as output_json:
        output_json.write(json.dumps(project_contributor_contributions, indent=4, sort_keys=False))


def collect_contribution_data(oss_repos_file_path: str, api_client: API) -> {}:
    """ reads the specified projects from `oss_repos_file_path` and gets their contributors'
    contribution counts (number of commits to repo)
    :returns a dict enriched with oss project data:
    { domain:
        { repo_owner: '', repo_name: '', domain: domain, company: '',
                contributors: <the contributors dict returned by get_stats_contributors()>
        }
    }
    """
    with open(oss_repos_file_path) as repos_json:
        data = json.load(repos_json)

        project_contributors = {}

        # for each of the selected projects (in oss_repos.json)
        for project in data.values():
            repo_owner = project['owner']     # e.g. 'flutter'
            repo_name = project['repo_name']  # e.g. 'flutter'
            domain = project['domain']        # e.g. 'dart' -> the actual language used in other projects
            company = project['company']      # e.g. 'google'

            # get top 100 contributors of domain repo and the number of their commits to it
            stats_contributor_nr_commits = get_stats_contributors(
                repo_owner=repo_owner, repo_name=repo_name, api_client=api_client
            )

            project_contributors[domain] = dict(
                repo_owner=repo_owner, repo_name=repo_name, domain=domain, company=company,
                contributors=stats_contributor_nr_commits
            )

            number_domain_contributors = len(stats_contributor_nr_commits)
            print('Getting contributor contribution counts for',
                  '{}/{}.'.format(repo_owner, repo_name),
                  '{} contributors found.'.format(number_domain_contributors))

        cache_contributor_stats_to_json(project_contributor_contributions=project_contributors)
        return project_contributors
