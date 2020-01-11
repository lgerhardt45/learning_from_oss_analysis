import json
import os
import sys
from itertools import islice
import requests

import util as util
from model.observation import Observation


# helper methods
def take(n, iterable):
    """ Return first n items of the iterable as a list """
    return list(islice(iterable, n))


class ContributorAnalysis:
    _api_token: str
    _output_file_path: str
    _slice_amount: int
    _github_base_url: str
    _project_contributors: {str: [{str: str}]} = {}

    def __init__(self):
        self._github_base_url = 'https://api.github.com'
        self.setup()

    # UTILITY METHODS
    def setup(self):
        print('setting up')
        # get config
        with open('config.json') as config:
            config_json = json.load(config)
            # api_token for authorization
            self._api_token = config_json['api_token']
            util.api_token = self._api_token
            # only first n observations for debugging purposes
            self._slice_amount = config_json['debug_slice_amount']
            # setup output file
            self._output_file_path = config_json['output_file_name']
            self.setup_output_file()
        print('done setting up')

    def setup_output_file(self):
        print('setting up output file')
        if os.path.exists(self._output_file_path):
            try:
                os.remove(self._output_file_path)
                print('removed old output file')
            except IOError:
                print('failed to remove old output file')
                return

        with open(self._output_file_path, mode='a') as csv:
            try:
                # write header
                sample_observation_for_header = Observation(0.0, 0, 0, False, False, '', '')
                csv.write(sample_observation_for_header.get_attribute_names_comma_delimited() + '\n')
            except IOError:
                print('Cannot write to output file')
                sys.exit(1)

    def export_observation_to_csv(self, observation: Observation):
        try:
            with open(self._output_file_path, mode='a') as csv:
                csv.write(observation.get_values_comma_delimited() + '\n')
        except IOError as e:
            print(e)
            print('failed to write %s to %s' % (repr(observation), self._output_file_path))
            self.tear_down()

    def save_contributor_stats_to_json(self):
        if os.path.exists(util.json_file_path):
            try:
                os.remove(util.json_file_path)
                print('removed old json file')
            except IOError:
                print('failed to remove old json file')
                return
        with open(util.json_file_path, mode='a') as output_json:
            output_json.write(json.dumps(self._project_contributors, indent=4, sort_keys=False))

    def tear_down(self):
        print('tearing down')
        if os.path.exists(self._output_file_path):
            os.remove(self._output_file_path)
            print('output file %s removed' % self._output_file_path)

    def get(self, url: str):
        """
        making GET requests adding authorization header
        :returns the full response from `requests.get()`
        """
        response = requests.get(url=url, headers={'Authorization': 'token %s' % self._api_token})
        print('Getting %s, response code: %i' % (url, response.status_code))
        if not (response or response.status_code == 404):
            # escape public org member request (returns 404) (not too nice)
            print('Failed request: %s' % response)

        return response

    # DATA COLLECTION METHODS
    def get_stats_contributors(self, repo_owner: str, repo_name: str) -> {str: int}:
        """
        via GET /repos/:owner/:repo/stats/contributors
        :returns a dictionary with key: user_name and value: number of commits to repo
        """
        stats_contributors_url = '{base_url}/repos/{repo_owner}/{repo_name}/stats/contributors'.format(
            base_url=self._github_base_url, repo_owner=repo_owner, repo_name=repo_name)

        # the top 100 contributors to the repo
        contributors = self.get(stats_contributors_url).json()
        repo_contributor_contributions = {}
        for contributor in contributors:
            contributor_name = contributor['author']['login']
            repo_contributor_contributions[contributor_name] = contributor['total']
        return repo_contributor_contributions

    def run(self):
        with open('repos.json') as repos_json:
            data = json.load(repos_json)

            # for each of the selected projects (in repos.json)
            for project in data.values():
                repo_owner = project['owner']     # e.g. 'flutter'
                repo_name = project['repo_name']  # e.g. 'flutter'
                domain = project['domain']        # e.g. 'dart' -> the actual language used in other projects
                company = project['company']      # e.g. 'google'

                print('repository:', '{}/{}'.format(repo_owner, repo_name))

                # get top 100 contributors of domain repo and the number of their commits to it
                stats_contributor_nr_commits = self.get_stats_contributors(repo_owner=repo_owner, repo_name=repo_name)
                self._project_contributors[domain] = dict(
                    repo_owner=repo_owner, repo_name=repo_name, domain=domain, company=company,
                    contributors=stats_contributor_nr_commits
                )

            self.save_contributor_stats_to_json()