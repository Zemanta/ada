import requests

from django.conf import settings


URL_BASE = 'https://one.zemanta.com'
URL_SIGNIN = '/signin'
URL_ACCOUNTS_OVERVIEW = '/api/accounts/overview/'


class ZemantaOne(object):

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['referer'] = URL_BASE
        self.login()

    def login(self):
        signin_get = self.session.get(URL_BASE + URL_SIGNIN)
        csrf_token = signin_get.cookies['csrftoken']
        r = self.session.post(URL_BASE + URL_SIGNIN,
            data={
                'username': settings.Z1_USERNAME,
                'password': settings.Z1_PASSWORD,
                'csrfmiddlewaretoken': csrf_token,
            },
        )
        if r.status_code != 200:
            raise Exception("Failed to log in to Zemanta One!")

    def all_accounts_overview(self):
        r = self.session.get(URL_BASE + URL_ACCOUNTS_OVERVIEW)
        return r
