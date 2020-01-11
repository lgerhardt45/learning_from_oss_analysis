import json

from api.api import API
from model.observation import Observation
import contributor_details_collector
import contribution_collector
import csv_writer


def setup():
    """ :returns the api client configured with the api token"""
    print('setting up')

    # get config
    with open('config.json') as config:
        config_json = json.load(config)

        api_token = config_json['api_token']  # for Github API authorization
        api = API(api_token=api_token)
        output_file_path = config_json['output_file_name']
        print('done setting up')
        return api, output_file_path


def main():
    api, output_file_path = setup()

    oss_contributions: {} = contribution_collector.collect_contribution_data(
        oss_repos_file_path='oss_repos.json', api_client=api
    )

    observations: [Observation] = contributor_details_collector.collect_contributor_details(
        domain_contributor_contributions=oss_contributions, api_client=api
    )
    csv_writer.export_observations_to_csv(observations=observations, output_file_path=output_file_path)
    print('done!')


if __name__ == '__main__':
    main()
