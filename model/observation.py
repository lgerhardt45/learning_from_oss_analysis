class Observation:
    def __init__(self,
                 average_stars: float,
                 nr_of_commits_to_project: int,
                 nr_of_projects_in_domain: int,
                 employed_at_domain_owner: bool,
                 has_project_in_domain: bool,
                 domain_name: str,
                 domain_owner: str):
        self._average_stars = average_stars
        self._domain_contribution = nr_of_commits_to_project
        self._nr_projects_in_domain = nr_of_projects_in_domain
        self._employed_at_domain_owner = employed_at_domain_owner
        self._has_project_in_domain = has_project_in_domain
        self._domain = domain_name
        self.domain_owner = domain_owner
