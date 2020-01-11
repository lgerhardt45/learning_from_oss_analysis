import requests


class API:
    _api_token: str

    def __init__(self, api_token: str):
        self._api_token = api_token

    def get(self, url: str):
        """
        making GET requests adding authorization header
        :returns the full response from `requests.get()`
        """
        response = requests.get(url=url, headers={'Authorization': 'token %s' % self._api_token})
        print('Getting %s, response code: %i' % (url, response.status_code))
        if not response:
            print('Failed request: %s' % response.json())

        return response
