import time

from slackclient import SlackClient

from django.core.management.base import BaseCommand
from django.conf import settings

slack_client = SlackClient(settings.SLACK_BOT_TOKEN)
AT_BOT = "<@" + settings.BOT_ID + ">"


class Command(BaseCommand):
    help = 'Runs slack real-time messaging bot'

    def handle(self, *args, **options):
        READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
        if slack_client.rtm_connect():
            print("StarterBot connected and running!")
            while True:
                command, channel = parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    handle_command(command, channel)
                time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    print(slack_rtm_output)
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and (AT_BOT in output['text'] or output['channel'] == settings.BOT_ID):
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    print("responding to: ", command, channel)
    response = "Hi!"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)
