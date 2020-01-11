import json

from data_collection.api.api import API
from data_collection.model.observation import Observation
from data_collection import contribution_collector, contributor_details_collector, csv_writer


def setup():
    """ :returns the api client configured with the api token"""

    # get config
    with open('config.json') as config:
        config_json = json.load(config)

        api_token = config_json['api_token']  # for Github API authorization
        api = API(api_token=api_token)
        output_file_path = config_json['output_file_name']
        return api, output_file_path


def main():
    api, output_file_path = setup()

    # oss_contributions: {} = contribution_collector.collect_contribution_data(
    #     oss_repos_file_path='data_collection/oss_repos.json', api_client=api
    # )

    # for debug: load cached oss contributions:
    oss_contributions = {}
    cached_contributions_json_file_path: str = 'domain_contributors_contributions.json'
    with open(cached_contributions_json_file_path) as data_json:
        oss_contributions = json.load(data_json)

    observations: [Observation] = contributor_details_collector.collect_contributor_details(
        domain_contributor_contributions=oss_contributions, api_client=api
    )
    print('Found %s observations in %s projects:' % (
        len(observations), len(oss_contributions)
    ))
    csv_writer.export_observations_to_csv(observations=observations, output_file_path=output_file_path)
    print('Done!')


if __name__ == '__main__':
    main()
