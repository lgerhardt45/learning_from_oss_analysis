import csv
import os
import sys
import util as util
from model.observation import Observation


class CSVWriter:

    def __init__(self, observations: [Observation]):
        self._observations = observations
        self._output_file_path = util.output_file_path

    def run(self):
        self.setup_output_file()
        self.export_observations_to_csv()

    def setup_output_file(self):
        print('setting up output file')
        if os.path.exists(self._output_file_path):
            try:
                os.remove(self._output_file_path)
                print('removed old output file')
            except IOError:
                print('failed to remove old output file')
                return

        if not self._observations:
            raise Exception('No observations found.')

        with open(self._output_file_path, mode='a') as csv_file:
            try:
                # write header
                csv_file.write(self._observations[0].get_attribute_names_comma_delimited() + '\n')
                print('done setting up output file')
            except IOError as ioe:
                print('cannot write to output file: %s' % ioe)
                sys.exit(1)

    def export_observations_to_csv(self):
        for observation in self._observations:
            with open(self._output_file_path, mode='a') as csv_file:
                try:
                    csv_file.write(observation.get_values_comma_delimited() + '\n')
                except IOError as ioe:
                    print('failed to write %s to %s' % (repr(observation), self._output_file_path))
                    print(ioe)
                    sys.exit(1)
