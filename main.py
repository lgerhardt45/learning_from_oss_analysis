import json

from util import util
import contribution_collector
from csv_writer import CSVWriter
import util as util


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
    CSVWriter().run


if __name__ == '__main__':
    main()
