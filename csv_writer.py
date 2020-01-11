from model.observation import Observation
import csv

class CSVWriter:


    def __init__(self, observations: []):
        self._observations = observations

    def write_observations_to_csv(self):
        if not self._observations:
            raise Exception('No observations found')
