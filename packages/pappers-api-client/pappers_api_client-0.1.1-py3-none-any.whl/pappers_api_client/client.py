import requests as rq

from pappers_api_client import utils, resources


class Client:
    BASE_URL = 'https://api.pappers.fr'

    def __init__(self, api_key, version='v2'):

        self._session = rq.Session()
        self._session._auth_params = {
            'api_token': api_key
        }

        self._base_url = utils.urljoin(
            self.BASE_URL, version
        )
        self._resources = {
            'recherche': resources.QueryPool(
                utils.urljoin(
                    self._base_url, 'recherche'
                ),
                self._session
            )
        }

    @property
    def resources(self):
        return self._resources
    
    @property
    def recherche(self):
        return self._resources['recherche']