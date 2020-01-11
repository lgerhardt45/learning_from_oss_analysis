import json

from util import util
from model.observation import Observation
import contributor_details_collector
import contribution_collector
import csv_writer


def setup(self):
    print('setting up')

    # get config
    with open('config.json') as config:
        config_json = json.load(config)

        util.api_token = config_json['api_token']  # for Github API authorization
        util.output_file_path = config_json['output_file_name']

    print('done setting up')


def main():
    oss_contributions: {} = contribution_collector.collect_contribution_data(oss_repos_file_path='oss_repos.json')
    observations: [Observation] = contributor_details_collector.collect_contributor_details(
        domain_contributor_contributions=oss_contributions
    )


if __name__ == '__main__':
    main()
