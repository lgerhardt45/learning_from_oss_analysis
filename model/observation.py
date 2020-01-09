class Observation:
    def __init__(self,
                 average_stars: float,
                 nr_of_commits_to_project: int,
                 nr_of_projects_in_domain: int,
                 employed_at_domain_owner: bool,
                 has_project_in_domain: bool,
                 domain_name: str,
                 domain_owner: str):
        self.average_stars: float = average_stars
        self.domain_contribution: int = nr_of_commits_to_project
        self.nr_projects_in_domain: int = nr_of_projects_in_domain
        self.employed_at_domain_owner: int = 1 if employed_at_domain_owner else 0
        self.has_project_in_domain: int = 1 if has_project_in_domain else 0
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

