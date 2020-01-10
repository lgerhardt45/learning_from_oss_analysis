import json
import os
import requests

from model.observation import Observation


class ContributorAnalysis:
    _github_base_url = 'https://api.github.com'
    _api_token = ''
    _observations: [Observation] = []
    _output_file_path = 'observations.csv'

    def get(self, url: str):
        """
        making GET requests adding authorization header
        :returns the full response from `requests.get()`
        """
        response = requests.get(url=url, headers={'Authorization': 'token %s' % self._api_token})
        print('Getting %s, response code: %i' % url, response.status_code)

        return response

    def user_is_public_member_of_org(self, user_id: str, organization_id: str) -> bool:
        """ via GET /orgs/:org/public_members/:username"""

        public_membership_url = '{base_url}/orgs/{org}/public_members/{user_name}'.format(
            base_url=self._github_base_url, org=organization_id, user_name=user_id
        )
        # https://developer.github.com/v3/orgs/members/#check-public-membership
        # returns with 204 if user is public member, 404 otherwise
        is_public_member_response = self.get(public_membership_url)

        return True if is_public_member_response.status_code == 204 else False

    def get_stats_contributors(self, repo_owner: str, repo_name: str) -> {str: int}:
        """
        via GET /repos/:owner/:repo/stats/contributors
        :returns a dictionary with key: user_name and value: number of commits to repo
        """
        stats_contributors_url = '{base_url}/repos/{repo_owner}/{repo_name}/stats/contributors'.format(
            base_url=self._github_base_url, repo_owner=repo_owner, repo_name=repo_name)

        # the top 100 contributors to the repo
        contributors = self.get(stats_contributors_url).json()

        return {contributor['author']['login']: contributor['total'] for contributor in contributors}

    def get_observation_entity(self, user_name: str, domain_name: str, organization_name: str,
                               no_contributor_commits: int):
        """
        via GET /users/:username/repos
        collects the necessary information for an Observation
        """

        # get all repos of a contributor
        contributor_repos_url = '{base_url}/users/{user_name}/repos'.format(
            base_url=self._github_base_url, user_name=user_name
        )
        contributor_repos = self.get(contributor_repos_url).json()

        total_stargazers = 0  # number of stars on repo
        total_projects_in_domain = 0
        employed_at_project_owner = False

        for contributor_repo in contributor_repos:
            language = None  # the repo's main programming language
            topics = [str]  # the project's (self assigned) topics that commonly represent the used framework

            if 'topic' in contributor_repo.keys():  # if project has no topic, key doesn't exist
                topics = (topic.lower() for topic in contributor_repo['topics'])
            if contributor_repo['language'] is not None:
                language = contributor_repo['language'].lower()

            # contributor's project is in the domain? (written in the oss language or with the oss framework)
            if (domain_name is language and language is not None) or domain_name in topics:
                total_projects_in_domain += 1
                total_stargazers += contributor_repo['stargazers_count']
                if not employed_at_project_owner:  # if already proven contributor is employed, save API call
                    employed_at_project_owner = self.user_is_public_member_of_org(
                        user_id=user_name, organization_id=organization_name
                    )
            else:
                continue
        observation = Observation(
            average_stars=0 if total_projects_in_domain == 0 else total_stargazers / total_projects_in_domain,
            nr_of_commits_to_project=no_contributor_commits,
            nr_of_projects_in_domain=total_projects_in_domain,
            employed_at_domain_owner=employed_at_project_owner,
            has_project_in_domain=True if total_projects_in_domain > 0 else False,
            domain_name=domain_name,
            domain_owner=organization_name)
        print('observation: %s' % repr(observation))
        return observation

    def export_to_csv(self):
        print('Writing to csv')

        with open(self._output_file_path, mode='a') as csv:
            if not self._observations:
                print('No observations gathered')
                return

            # write header
            csv.write(self._observations[0].get_attribute_names_comma_delimited())

            # write observations
            for observation in self._observations:
                csv.write(observation.get_values_comma_delimited())

    def setup(self):
        print('setting up')
        with open('config.json') as config:
            self._api_token = json.load(config)['api_token']

    def tear_down(self):
        print('tearing down')
        if os.path.exists(self._output_file_path):
            os.remove(self._output_file_path)
            print('output file %s removed' % self._output_file_path)

    def run(self):
        self.setup()

        with open('repos.json') as repos_json:
            data = json.load(repos_json)

            # for each of the selected projects (in repos.json)
            for project in data.values():
                repo_name = project['repo_name']  # e.g. 'apple/swift'
                repo_owner = project['owner']  # e.g. 'swift' -> used to check for language/ topic in github projects
                print('repository:', '{}/{}'.format(repo_owner, repo_name))

                # get top 100 contributors of domain repo and the number of their commits to it
                stats_contributor_nr_commits = self.get_stats_contributors(repo_owner=repo_owner, repo_name=repo_name)

                # get data on contributors' repositories
                for contributor_id, nr_commits in stats_contributor_nr_commits.items():
                    self._observations.append(self.get_observation_entity(user_name=contributor_id,
                                                                          domain_name=repo_name,
                                                                          organization_name=repo_owner,
                                                                          no_contributor_commits=nr_commits))

        print('{} observations on {} projects'.format(len(self._observations), len(data.values())))

        self.export_to_csv()
        print('>>> done')


if __name__ == '__main__':
    ContributorAnalysis().run()
