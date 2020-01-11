import os
import sys

from model.observation import Observation


def export_observations_to_csv(observations: [Observation], output_file_path: str):
    if not observations:
        raise Exception('No observations found.')
    _setup_output_file(sample_observation=observations[0], output_file_path=output_file_path)
    _write_observations_to_csv(observations=observations, output_file_path=output_file_path)


def _setup_output_file(sample_observation: Observation, output_file_path: str):
    print('Setting up output file')
    if os.path.exists(output_file_path):
        try:
            os.remove(output_file_path)
            print('Removed old output file')
        except IOError:
            print('Failed to remove old output file')
            return

    with open(output_file_path, mode='a') as csv_file:
        try:
            # write header
            csv_file.write(sample_observation.get_attribute_names_comma_delimited() + '\n')
        except IOError as ioe:
            print('Cannot write to output file: %s' % ioe)
            sys.exit(1)


def _write_observations_to_csv(observations: [Observation], output_file_path: str):
    with open(output_file_path, mode='a') as csv_file:
        for observation in observations:
            try:
                csv_file.write(observation.get_values_comma_delimited() + '\n')
            except IOError as ioe:
                print('Failed to write %s to %s' % (repr(observation), output_file_path))
                print(ioe)
                sys.exit(1)
