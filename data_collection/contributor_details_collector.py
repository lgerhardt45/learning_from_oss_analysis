from data_collection.api.api import API
from data_collection.model.observation import Observation


def project_in_domain(repo_languages: [], repo_topics: [], domain: str) -> bool:
    """ checks whether the domain is in the developer repo's languages to determine
    whether a project is in the domain (i.e. written in the same language
    as the developer contributed to). """
    repo_domains_lower = [repo_domain.lower().replace(" ", "") for repo_domain in repo_languages + repo_topics]  # [str]
    for repo_domain in repo_domains_lower:
        if domain in repo_domain:  # checks string in string for the case of topic = 'swift4', domain = 'swift'
            return True
    return False


def employed_at_domain_owner(company: str, user_company: str) -> bool:
    """ returns True, if the user works at the domain owner
    companies are often marked as '@company'"""
    if user_company in company.lower():
        return True
    return False


def prepare_query(users: []):
    """ prepares the GraphQL query for the users of a project
    :param users: the dict with all contributors for a project (as gathered in contribution_collector.py)"""

    # users = list(project_data['contributors'].keys())
    user_queries = ''
    for user in users:
        # The GraphQL query (with a few additional bits included) itself defined as a multi-line string.
        user_queries += get_single_user_query(user)
    return user_queries


def get_single_user_query(user_name: str) -> str:
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
                repositoryTopics(first: 5) {
                  nodes {
                    topic {
                      name
                    }
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
    """ The Github GraphQL api doesn't allow to identify sub-queries with non-letters
    or starting with a number in non-string attributes, such that 'user-name' or '4username' fails"""
    final = ''
    if string[0].isnumeric():
        string = string[1:]
    for char in string:
        if char.isalnum():
            final += char
    return final

def partition_list(items, count_per_partition=20):
    return [
		items[i:i+count_per_partition] for i in range(0, len(items), count_per_partition)
	]

def collect_contributor_details(domain_contributor_contributions: {}, api_client: API):
    """
    Uses Github's v4 API with GraphQL to lookup the last 10 own repos of the contributors.
    If the user does not work at the oss sponsoring company and has at least one project of which
    the main programming language is equal to the domain (i.e. the oss language), he is added as an
    `Observation`
    """

    observations = []  # each user is an observation if applicable

    # go over each oss project
    for project, project_data in domain_contributor_contributions.items():
        print('Getting observations for domain: %s' % project)

        # do 20 requests at a time
        users = list(project_data['contributors'].keys())
        partitioned_list = partition_list(users, 20)
        for part_users in partitioned_list:
            # the query is still done with non-normalized (see normalize()) usernames to get right user details
            user_queries = prepare_query(users=part_users)
            result = api_client.post_v4_query(user_queries)  # execute the query
            user_query_data = result['data']

            # the information about domain, company name and the number of contributions
            domain = project_data['domain']
            company = project_data['company']

            # the usernames had to be normalized for the query (see above)
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

                    # domain in main repo languages
                    repository_languages = repo['languages']['nodes']  # is a list of dicts: [{'name': Swift}]
                    repository_languages_list = [lang_dict['name'] for lang_dict in repository_languages]

                    # domain in main repo topics
                    repository_topics = repo['repositoryTopics']['nodes']
                    repository_topics_list = []
                    if repository_topics:  # not empty
                        repository_topics_list = [topic_dict['topic']['name'] for topic_dict in repository_topics]

                    # HERE WE GO: CHECK WHETHER DOMAIN IN LANGUAGES OR TOPICS
                    if project_in_domain(repo_languages=repository_languages_list,
                                         repo_topics=repository_topics_list, domain=domain):

                        # THAT'S THE ONE!
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
            # end of partitioned users (20 requests at a time)
        # end of each user of project
    # end of each project
    return observations
