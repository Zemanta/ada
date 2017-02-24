import nltk
nltk.download('punkt')
import logging
from unidecode import unidecode
import enum
import numpy as np
import math
from collections import Counter



logger = logging.getLogger(__name__)


class InputIntent(enum.Enum):
	LiveCampaings = 0
	SpendAmount = 1
	AdPerformance = 2
	CampaignPerformance = 3
	LiveAccounts = 4





d = {("Which campaigns are running currently?", "Which campaigns are live?") : InputIntent.LiveCampaings,
	 ("What was the spend on [campaign1] yesterday/last month/last week?", "What was [campaign1]'s yesterday spend?") : InputIntent.SpendAmount,
	 ("Which ad has best performance in [campaign1]?", "Which is the best performing ad in [campaign1]") : InputIntent.AdPerformance,
	 ("How is [campaign1] doing?") : InputIntent.CampaignPerformance,
	 ("Which accounts are running currently?", "Which accounts are currently live?", "Which accounts are currently active?") : InputIntent.LiveAccounts}

stop_tokens = ["?", "]", ".", "!"]


class Response(object):
	text = None
	def __init__(self, text):
		self.text = text

	def __eq__(self, text):
		return self.text == text

	def __repr__(self):
		'text={0}'.format(self.text)


class Parser(object):


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


	def get_similarity(self, input_tokens, questions):
		tokenized_questions = map(self.tokenize_input, questions)
		sim = 0
		for q in tokenized_questions:
			curr_sim = self.get_cosine(Counter(q), Counter(input_tokens))
			sim = max(sim, curr_sim)
		return sim

	def get_input_intent(self, input_tokens):
		input_intent = None
		sim = 0
		for (questions, intent) in d.items():
			curr_sim = self.get_similarity(input_tokens, questions)
			if curr_sim > sim:
				sim = curr_sim
				input_intent = intent
		return input_intent




class Chatter(object):

	def __init__(self):
		self.parser = Parser()


	def respond(self, text):
		tokens = self.parser.tokenize_input(text)
		tokens = [token for token in tokens if token not in stop_tokens]
		input_intent = self.parser.get_input_intent(tokens)


		if input_intent == InputIntent.LiveCampaings:
			print("Live Campaings")



		elif input_intent == InputIntent.SpendAmount:
			ix = tokens.index("[")
			campaign = tokens[ix+1]


		elif input_intent == InputIntent.AdPerformance:
			ix = tokens.index("[")
			campaign = tokens[ix+1]














Chatter().respond("Whichh campaigns aree elive?")
