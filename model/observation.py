import json


class Observation:
    def __init__(self,
                 user_name: str,
                 average_stars: float,
                 nr_of_commits_to_project: int,
                 nr_of_projects_in_domain: int,
                 nr_of_projects_in_total: int,
                 employed_at_domain_owner: bool,
                 domain_name: str,
                 domain_owner: str):
        self.user_name: str = user_name
        self.average_stars: float = average_stars
        self.domain_contribution: int = nr_of_commits_to_project
        self.nr_projects_in_domain: int = nr_of_projects_in_domain
        self.nr_of_projects_in_total: int = nr_of_projects_in_total
        self.employed_at_domain_owner: int = 1 if employed_at_domain_owner else 0
        self.domain = domain_name
        self.domain_owner = domain_owner

    def get_attribute_names_comma_delimited(self) -> str:
        """ returns all attribute names to be used for the header of the observations csv file"""
        return ','.join(self.__dict__.keys())

    def get_values_comma_delimited(self):
        """
        represents entity as comma-delimited string for writing to a csv file
        decimal separator is '.'
        """
        return ','.join([str(value) for value in self.__dict__.values()])

    def __repr__(self):
        return '<Observation: %s>' % json.dumps(self.__dict__)
