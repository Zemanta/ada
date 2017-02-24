import requests

from django.conf import settings


URL_BASE = 'https://one.zemanta.com'
URL_SIGNIN = '/signin'
URL_ACCOUNTS_OVERVIEW = '/api/accounts/overview/'
URL_ACCOUNT_CAMPAIGNS = '/api/accounts/{id}/breakdown/campaign/'


class ZemantaOne(object):

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['referer'] = URL_BASE
        self.session.hooks['pre_request'] = add_csrf
        self.login()

    def get(self, *args, **kwargs):
        return self.session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        csrf_token = self.session.cookies.get('csrftoken')
        self.session.headers['X-CSRFToken'] = csrf_token
        return self.session.post(*args, **kwargs)

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
        r = self.get(URL_BASE + URL_ACCOUNTS_OVERVIEW)
        return r

    def get_running_campaigns(self, account_id):
        r = self.post(URL_BASE + URL_ACCOUNT_CAMPAIGNS.format(id=account_id),
            json={
                'params': {
                    'parents': [],
                    'start_date': '2017-02-23',
                    'end_date': '2017-01-24',
                    'show_archived': False,
                    'level': 1,
                    'limit': 60,
                    'offset': 0,
                    'order': '-e_yesterday_cost',
                }
            }
        )
        return r
