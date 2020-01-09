import json
import requests
from pprint import pprint

from model.observation import Observation

github_base_url = 'https://api.github.com'


def user_is_public_member_of_org(user_id: str, organization_id: str) -> bool:
    """ via GET /orgs/:org/public_members/:username"""

    public_membership_url = '{base_url}/orgs/{org}/public_members/{user_name}'.format(
        base_url=github_base_url, org=organization_id, user_name=user_id
    )
    # https://developer.github.com/v3/orgs/members/#check-public-membership
    # returns with 204 if user is public member, 404 otherwise
    is_public_member_response = requests.get(public_membership_url)

    return True if is_public_member_response.status_code == 204 else False


def get_stats_contributors(repo_owner: str, repo_name: str) -> {str: int}:
    """
    via GET /repos/:owner/:repo/stats/contributors
    :returns a dictionary with key: user_name and value: number of commits to repo
    """
    stats_contributors_url = '{base_url}/repos/{repo_owner}/{repo_name}/stats/contributors'.format(
        base_url=github_base_url, repo_owner=repo_owner, repo_name=repo_name)

    # the top 100 contributors to the repo
    contributors = requests.get(stats_contributors_url).json()

    return {contributor['author']['login']: contributor['total'] for contributor in contributors}


def get_observation_entity(user_name: str, domain_name: str, organization_name: str,
                           no_contributor_commits: int):
    """
    via GET /users/:username/repos
    collects the necessary information for an Observation
    """

    # get all repos of a contributor
    contributor_repos_url = '{base_url}/users/{user_name}/repos'.format(
        base_url=github_base_url, user_name=user_name
    )
    contributor_repos = requests.get(contributor_repos_url).json()

    total_stargazers = 0  # number of stars on repo
    total_projects_in_domain = 0
    employed_at_project_owner = False

    for contributor_repo in contributor_repos:
        language = contributor_repo['language'].lower()  # the repo's main programming language
        topics = [str]  # the project's (self assigned) topics that commonly represent the used framework

        if 'topic' in contributor_repo.keys():  # if project has no topic, key doesn't exist
            topics = (topic.lower() for topic in contributor_repo['topics'])

        # contributor's project in the domain
        if domain_name is language or domain_name in topics:
            total_projects_in_domain += 1
            total_stargazers += contributor_repo['stargazers_count']
            if not employed_at_project_owner:  # if already proven contributor is employed, save API call
                employed_at_project_owner = user_is_public_member_of_org(
                    user_id=user_name, organization_id=organization_name
                )

    return Observation(average_stars=total_stargazers / total_projects_in_domain,
                       nr_of_commits_to_project=no_contributor_commits,
                       nr_of_projects_in_domain=total_projects_in_domain,
                       employed_at_domain_owner=employed_at_project_owner,
                       has_project_in_domain=True if total_projects_in_domain > 0 else False,
                       domain_name=domain_name,
                       domain_owner=organization_name)


def main():
    observations = [Observation]

    with open('repos.json') as repos_json:
        data = json.load(repos_json)

        # for each of the selected projects (in repos.json)
        for project in data.values():
            repo_name = project['repo_name']  # e.g. 'apple/swift'
            repo_owner = project['owner']  # e.g. 'swift' -> used to check for language/ topic in github projects
            print('repository:', '{}/{}'.format(repo_owner, repo_name))

            # get top 100 contributors of domain repo and the number of their commits to it
            stats_contributor_nr_commits = get_stats_contributors(repo_owner=repo_owner, repo_name=repo_name)

            # get data on contributors' repositories
            for contributor_id, nr_commits in stats_contributor_nr_commits.items():
                observations.append(get_observation_entity(user_name=contributor_id,
                                                           domain_name=repo_name,
                                                           organization_name=repo_owner,
                                                           no_contributor_commits=nr_commits))

    print('{} observations on {} projects'.format(len(observations), len(data.values())))
    print('Writing to csv')


if __name__ == '__main__':
    main()
