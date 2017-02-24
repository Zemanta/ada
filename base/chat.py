import nltk
import logging
from unidecode import unidecode
import enum
import math
from collections import Counter
from wit import Wit
from base.spell import correction
import datetime

logger = logging.getLogger(__name__)
token="K3HP47EPDBH3OULNFOP2RDQNMCQFCRXR"


CONTEXT = {}


class InputIntent(enum.Enum):
    LiveCampaings = 0
    SpendAmount = 1
    AdPerformance = 2
    CampaignPerformance = 3
    LiveAccounts = 4
    StopCampaign = 5

d = {("Which campaigns are running currently?", "Which campaigns are live?") : InputIntent.LiveCampaings,
     ("What was the spend on campaign [13218]", "What was campaign [1233]'s spend?") : InputIntent.SpendAmount,
     ("Which ad has best performance in [campaign1]?", "Which is the best performing ad in [campaign1]") : InputIntent.AdPerformance,
     ("How is [campaign1] doing?",) : InputIntent.CampaignPerformance,
     ("Which accounts are running currently?", "Which accounts are currently live?", "Which accounts are currently active?") : InputIntent.LiveAccounts,
     ("Stop [campaign1].",) : InputIntent.StopCampaign}

stop_tokens = ["?", ".", "!"]


class Response(object):
    text = None
    def __init__(self, text):
        self.text = text

    def __eq__(self, text):
        return self.text == text

    def __repr__(self):
        'text={0}'.format(self.text)


class Parser(object):


    def __init__(self):
        self.client = Wit(access_token=token)


    def get_cosine(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    def tokenize_input(self, text):
        strip = text.strip().lower()
        normalized = unidecode(strip)
        return nltk.word_tokenize(normalized)


    def get_similarity_for_intent(self, input_tokens, questions):
        similarities = [self.get_cosine(Counter(self.tokenize_input(question)), Counter(input_tokens)) for question in questions]
        return max(similarities)

    def get_input_intent(self, input_tokens):
        intents_by_sim = [(intent, self.get_similarity_for_intent(input_tokens, questions)) for (questions, intent) in d.items()]
        print(intents_by_sim)
        return max(intents_by_sim, key=lambda x:x[1])[0]

    def get_datetime(self, tokens):
        message = ' '.join(tokens)
        resp = self.client.message(message)
        try:
            datetimes = resp['entities']['datetime']
            for date in datetimes:
                datetime_from = datetime.datetime.strptime(date['value'][:-6], "%Y-%m-%dT%H:%M:%S.%f")
                grain = date['grain']
                datetime_to = None
                if grain == "day" or grain == "minute":
                    datetime_to = datetime_from
                elif grain == "week":
                    datetime_to = datetime_from + datetime.timedelta(weeks=1)
                elif grain == "month":
                    datetime_to = datetime_from + datetime.timedelta(month=1)
                elif grain == "year":
                    datetime_to = datetime_from + datetime.tiemdelta(year=1)

                return (datetime_from, datetime_to)
        except KeyError:
            return None

    def get_campaign(self, tokens):
        campaign_id = None
        for token in tokens:
            try:
                campaign_id = int(token)
                break
            except:
                pass
        return campaign_id


class Chatter(object):

    def __init__(self, z1):
        self.parser = Parser()
        self.z1 = z1


    def respond(self, text):
        tokens = self.parser.tokenize_input(text)
        tokens = [correction(token) for token in tokens if token not in stop_tokens]
        campaign = self.parser.get_campaign(tokens)
        datetime = self.parser.get_datetime(tokens)

        if CONTEXT.get('missingDatetime'):
            res = self.parser.get_datetime(tokens)
            if res:
                input_intent = CONTEXT['missingDatetime']['intent']
                campaign = CONTEXT['missingDatetime']['campaign_id']
                del CONTEXT['missingDatetime']
            else:
                return "When?"
        if CONTEXT.get('missingCampaign'):
            campaign = self.parser.get_campaign(tokens)
            if campaign:
                input_intent = CONTEXT['missingCampaign']['intent']
                datetime = CONTEXT['missingCampaign']['datetime']
                del CONTEXT['missingCampaign']
            else:
                return "Which campaign?"
        else:
            input_intent = self.parser.get_input_intent(tokens)

        print("Selected intent: ", input_intent)

        if input_intent == InputIntent.LiveCampaings:
            live_campaigns = self.z1.get_running_campaigns(92)
            if live_campaigns:
                return "The following campaigns are currently live: \n" + '\n'.join('- ' + x for x in live_campaigns)
            else:
                return "None of your campaigns are currently active!"

        elif input_intent == InputIntent.SpendAmount:
            if not datetime and not campaign:
                return "WHAT?!"
            if not datetime:
                CONTEXT['missingDatetime'] = {'campaign_id': campaign, 'intent': input_intent}
                return "When?"
            if not campaign:
                CONTEXT['missingCampaign'] = {'datetime': datetime, 'intent': input_intent}
                return "On which campaign?"
            (start_date, end_date) = datetime
            campaign_spend = self.z1.get_campaign_spend(campaign, start_date, end_date)
            return "Spend on campaign {0} was {1}$".format(campaign, campaign_spend)

        elif input_intent == InputIntent.AdPerformance:
            if not campaign:
                return "Please specify Campaign's ID"
            r = self.z1.get_content_insights(campaign)
            title = r['best_performer_rows'][0]['summary']
            return "The best performing ad in campaign {campaign_id} is '{title}'".format(
                campaign_id=campaign,
                title=title
            )
