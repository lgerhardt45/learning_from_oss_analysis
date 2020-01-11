import requests


class API:
    _api_token: str
    _github_v3_api_base_url = 'https://api.github.com/'
    _github_v4_api_base_url = 'https://api.github.com/graphql/'

    def __init__(self, api_token: str):
        self._api_token = api_token

    def get_v3(self, url: str):
        """
        making GET requests to Github's v3 API (https://api.github.com) adding authorization header
        :returns the full response from `requests.get()`
        """
        full_url = self._github_v3_api_base_url + url
        response = requests.get(url=url, headers={'Authorization': 'token %s' % self._api_token})
        print('Getting %s, response code: %i' % (url, response.status_code))
        if not response:
            print('Failed request: %s' % response.json())

        return response
