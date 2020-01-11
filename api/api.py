import requests


class API:
    _api_token: str
    _github_v3_api_base_url = 'https://api.github.com/'
    _github_v4_api_base_url = 'https://api.github.com/graphql'

    def __init__(self, api_token: str):
        self._api_token = api_token

    def get_v3(self, url: str):
        """
        Makes an authorized GET requests to Github's v3 API (https://api.github.com) adding authorization header
        :returns the full response from `requests.get()`
        """

        full_url = self._github_v3_api_base_url + url
        response = requests.get(url=full_url, headers={'Authorization': 'token %s' % self._api_token})
        print('Getting %s, response code: %i' % (url, response.status_code))
        if not response:
            print('Failed request: %s' % response.json())

        return response

    def post_v4_query(self, query):
        """
        Makes an authorized POST request to Github's v4 API (https://api.github.com/graphql)
        The query is inserted as string as the json= argument """

        headers = {"Authorization": "bearer %s" % self._api_token}
        actual_query = '{' + query + '}'
        request = requests.post(self._github_v4_api_base_url, json={'query': actual_query}, headers=headers)
        if request.status_code == 200 and 'errors' not in request.json().keys():
            return request.json()
        else:
            raise Exception(
                'Query failed to run (code of {code}). \nErrors: {errors}. \nQuery: {query}.'.format(
                    code=request.status_code, errors=request.json()['errors'], query=actual_query)
            )
