import requests
import datetime

from django.conf import settings


URL_BASE = 'https://one.zemanta.com'
URL_SIGNIN = '/signin'
URL_ACCOUNTS_OVERVIEW = '/api/accounts/overview/'
URL_ACCOUNT_CAMPAIGNS = '/api/accounts/{id}/breakdown/campaign/'
URL_CAMPAIGN_STATS = '/rest/v1/campaigns/{id}/stats/'


class ZemantaOne(object):

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['referer'] = URL_BASE
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
        today = datetime.date.today()
        r = self._get_account_campaign_breakdown(account_id, start_date=today, end_date=today)
        resp = r.json()
        return [row['breakdown_name'] for row in resp['data'][0]['rows'] if row['status']['value'] == 1]

    def _get_account_campaign_breakdown(self, account_id, start_date, end_date):
        r = self.post(URL_BASE + URL_ACCOUNT_CAMPAIGNS.format(id=account_id),
            json={
                'params': {
                    'parents': [],
                    'start_date': start_date.isoformat(),
                    'end_d.ate': end_date.isoformat(),
                    'show_archived': False,
                    'level': 1,
                    'limit': 60,
                    'offset': 0,
                    'order': '-e_yesterday_cost',
                }
            }
        )
        return r

    def get_campaign_spend(self, campaign_id, start_date, end_date):
        params = {
            'from': start_date.isoformat(),
            'to': end_date.isoformat(),
        }
        r = self.get(URL_BASE + URL_CAMPAIGN_STATS.format(id=campaign_id), params=params)
        resp = r.json()
        return resp['data']['totalCost']
