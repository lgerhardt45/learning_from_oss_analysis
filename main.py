from contributor_analysis import ContributorAnalysis
from csv_writer import CSVWriter
import util as util


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
    print('done setting up')


def main():
    ContributorAnalysis().run()
    CSVWriter().run


if __name__ == '__main__':
    main()
