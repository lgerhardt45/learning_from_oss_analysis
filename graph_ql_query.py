import requests
import json
from pprint import pprint
import sys
import util as util
from model.observation import Observation


def project_in_domain(repo_languages: [], domain: str) -> bool:
    """ returns True, if the domain is in the repo languages i.e. the user has an
     own project in the domain of the oss project """
    languages_in_lower = [lang.lower() for lang in repo_languages]
    if domain in languages_in_lower:
        return True
    return False


def employed_at_domain_owner(company: str, user_company: str) -> bool:
    """ returns True, if the user works at the domain owner
    companies are often marked as '@company'"""
    if user_company in company.lower():
        return True
    return False


def prepare_query(project_data: dict):
    """ prepares the GraphQL query for the users of a project
    :param project_data: the dict with all contributors for a project (as gathered in contributor_analysis.py)"""

    users = list(project_data['contributors'].keys())
    user_queries = ''
    for user in users:
        # The GraphQL query (with a few additional bits included) itself defined as a multi-line string.
        user_queries += get_user_query(user)
    return user_queries


def get_user_query(user_name: str) -> str:
    return """%s: user(login: "%s") {
            company
            repositories(last: 10, isFork: false, ownerAffiliations: OWNER) {
              totalCount
              nodes {
                name
                languages(first: 3) {
                  nodes {
                    name
                  }
                }
                stargazers {
                  totalCount
                }
              }
            }
          }
          """ % (normalize(user_name), user_name)


def normalize(string: str) -> str:
    """ The Github GraphQL api doesn't allow queries with non-letters in non-string attributes,
    such that 'user-name' throws an error
    python does not have a str([char]) method"""
    final = ''
    for char in string:
        if char.isalpha():
            final += char
    return final


class GraphQLQuerying:
    """ for each project -> all contributors -> their stuff"""
    _domain_contributor_contributions: {}
    _headers = {"Authorization": "bearer %s" % util.api_token}

    def __init__(self, domain_contributor_contributions: dict):
        self._domain_contributor_contributions = domain_contributor_contributions

    def run_query(self, query):
        """ A simple function to use requests.post to make the API call. Note the json= section. """
        actual_query = '{' + query + '}'
        request = requests.post('https://api.github.com/graphql', json={'query': actual_query}, headers=self._headers)
        if request.status_code == 200 and 'errors' not in request.json().keys():
            return request.json()
        else:
            raise Exception(
                'Query failed to run (code of {code}). \nErrors: {errors}. \nQuery: {query}.'
                    .format(code=request.status_code, errors=request.json()['errors'], query=actual_query)
            )

    def run(self):
        observations = []  # each user is an observation if applicable

        # each project
        for project, project_data in list(self._domain_contributor_contributions.items()):
            print('Getting observations from project: %s' % project)

            user_queries = prepare_query(project_data=project_data)
            result = self.run_query(user_queries)  # Execute the query
            pprint(result)
            user_query_data = result['data']

            # the information about domain, company name and the number of contributions
            domain = project_data['domain']
            company = project_data['company']
            # the usernames had to be normalized for the query
            # so they are normalized for the number of contributions-lookup here
            user_contributions = {normalize(key): value for key, value in project_data['contributors'].items()}

            # each user is an observation: here goes the search :-)
            # note: user is the username and normalized
            for user, user_value in user_query_data.items():  # is a dict (key: user, value: company and repos)

                # start counting 'dem observations
                total_nr_of_repos_in_domain = 0
                total_nr_of_stars_on_domain_repos = 0
                repositories = user_value['repositories']['nodes']

                # now check for name, programming languages and number of stars of project
                for repo in repositories:  # is a list (all user repositories with name, languages, stargazers)
                    repository_name = repo['name']
                    repository_languages = repo['languages']['nodes']  # is a list of dicts: [{'name': Swift}]
                    repository_languages_list = [lang_dict['name'] for lang_dict in repository_languages]

                    # HERE WE GO: CHECK WHETHER DOMAIN IN LANGUAGES
                    if project_in_domain(repo_languages=repository_languages_list, domain=domain):
                        print('Found repo within domain: %s by %s 🥰' % (repository_name, user))
                        repository_stargazers = repo['stargazers']['totalCount']
                        total_nr_of_repos_in_domain += 1
                        total_nr_of_stars_on_domain_repos += repository_stargazers

                # done checking all contributor repos (non-forked, user is owner)
                # when user has a project(s) in the domain -> is an observation
                if total_nr_of_repos_in_domain > 0:

                    # Consider only outside collaborators on oss projects?
                    user_company = user_value['company']
                    is_employed_at_domain_owner = True
                    if user_company is None or not employed_at_domain_owner(company=company, user_company=user_company):
                        is_employed_at_domain_owner = False

                    average_stars_on_domain_repos = total_nr_of_stars_on_domain_repos / total_nr_of_repos_in_domain
                    nr_of_contributions_to_domain_project = user_contributions[user]
                    total_nr_of_repos = user_value['repositories']['totalCount']
                    observation = Observation(
                        user_name=user,
                        average_stars=average_stars_on_domain_repos,
                        nr_of_commits_to_project=nr_of_contributions_to_domain_project,
                        nr_of_projects_in_domain=total_nr_of_repos_in_domain,
                        nr_of_projects_in_total=total_nr_of_repos,
                        employed_at_domain_owner=is_employed_at_domain_owner,
                        domain_name=domain,
                        domain_owner=company,
                    )
                    observations.append(observation)
            # end of each user of project
        # end of each project
        print(
            '%s observations in %s projects found:' % (len(observations), len(self._domain_contributor_contributions)))
        for obs in observations:
            print(obs)


if __name__ == '__main__':
    with open(util.json_file_path) as data_json:
        domain_contributors_contributions = json.load(data_json)
        GraphQLQuerying(domain_contributor_contributions=domain_contributors_contributions).run()
