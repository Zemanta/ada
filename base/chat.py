import nltk
import logging
from unidecode import unidecode
import enum
import math
from collections import Counter
from spell import correction
from wit import Wit
from spell import correction
import datetime

logger = logging.getLogger(__name__)
token="K3HP47EPDBH3OULNFOP2RDQNMCQFCRXR"


class InputIntent(enum.Enum):
    LiveCampaings = 0
    SpendAmount = 1
    AdPerformance = 2
    CampaignPerformance = 3
    LiveAccounts = 4
    StopCampaign = 5

d = {("Which campaigns are running currently?", "Which campaigns are live?") : InputIntent.LiveCampaings,
     ("What was the spend on [campaign1] yesterday/last month/last week?", "What was [campaign1]'s yesterday spend?") : InputIntent.SpendAmount,
     ("Which ad has best performance in [campaign1]?", "Which is the best performing ad in [campaign1]") : InputIntent.AdPerformance,
     ("How is [campaign1] doing?") : InputIntent.CampaignPerformance,
     ("Which accounts are running currently?", "Which accounts are currently live?", "Which accounts are currently active?") : InputIntent.LiveAccounts,
     ("Stop [campaign1].") : InputIntent.StopCampaign}

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

    def get_datetime(self, message):
        resp = self.client.message(message)
        try:
            datetimes = resp['entities']['datetime']
            for date in datetimes:
                datetime_from = datetime.datetime.strptime(date['value'][:-6], "%Y-%m-%dT%H:%M:%S.%f")
                grain = date['grain']
                datetime_to = None
                if grain == "day":
                    datetime_to = datetime_from + datetime.timedelta(days=1)
                elif grain == "week":
                    datetime_to = datetime_from + datetime.timedelta(weeks=1)
                elif grain == "month":
                    datetime_to = datetime_from + datetime.timedelta(month=1)
                elif grain == "year":
                    datetime_to = datetime_from + datetime.tiemdelta(year=1)

                return (datetime_from, datetime_to)
        except KeyError:
            return None




class Chatter(object):

    def __init__(self):
        self.parser = Parser()


    def respond(self, text):
        tokens = self.parser.tokenize_input(text)
        tokens = [correction(token) for token in tokens if token not in stop_tokens]
        input_intent = self.parser.get_input_intent(tokens)

        print(self.parser.get_datetime(text))


        if input_intent == InputIntent.LiveCampaings:
            live_campaigns = self.z1.get_running_campaigns(92)
            if live_campaigns:
                return "The following campaigns are currently live: \n" + '\n'.join('- ' + x for x in live_campaigns)
            else:
                return "None of your campaigns are currently active!"

        elif input_intent == InputIntent.SpendAmount:
            ix = tokens.index("[")
            campaign = tokens[ix+1]

        elif input_intent == InputIntent.AdPerformance:
            ix = tokens.index("[")
            campaign = tokens[ix+1]


Chatter().respond("Show me campaings friday")
