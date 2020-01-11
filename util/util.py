import os
import json

api_token: str = ''
output_file_path: str = ''
github_v3_api_base_url = 'https://api.github.com'
github_v4_api_base_url = 'https://api.github.com/graphql'
cached_contributions_json_file_path: str = 'domain_contributors_contributions.json'


def cache_contributor_stats_to_json(project_contributor_contributions: {}):
    if os.path.exists(cached_contributions_json_file_path):
        try:
            os.remove(cached_contributions_json_file_path)
            print('removed old json file')
        except IOError:
            print('failed to remove old json file')
            return
    with open(cached_contributions_json_file_path, mode='a') as output_json:
        output_json.write(json.dumps(project_contributor_contributions, indent=4, sort_keys=False))
