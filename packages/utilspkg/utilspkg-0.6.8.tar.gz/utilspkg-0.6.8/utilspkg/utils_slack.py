import os
import time
# import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from utilspkg import utils_init

logger = utils_init.setup_logger(__name__)

if __name__ == '__main__':
    utils_init.load_env_variables_from_yaml('/Users/croft/VScode/ptagit/env_vars.yaml')

# not doing that since i supposedly set one up in the class itself? that's weird, I don't think I ever directly use it do it? logger = utils_init.setup_logger(__name__)

class SlackConnect:
    def __init__(self, api_key=None, testing_flag=False):
        """
        Initialize the SlackSender with an API key, testing flag, and optional logger.
        """
        # get the value of 'SLACK_API_KEY' from os if it exists
        self.SLACK_API_KEY = os.getenv("SLACK_API_KEY")

        # handle the old variable name for a while
        if not self.SLACK_API_KEY:
            self.SLACK_API_KEY = os.environ["SLACK_ACCESS_TOKEN_TEAM"]

        # I'm retiring TESTING_DM in favor of TESTING_CHANNEL, but handling it in the interim
        self.TESTING_CHANNEL = os.getenv ("TESTING_DM")

        # handle the old variable name for a while
        if not self.TESTING_CHANNEL:
            self.TESTING_CHANNEL = os.environ["TESTING_CHANNEL"] # not currently used since all goes to the DM's "channel"

        self.api_key = api_key if api_key else self.SLACK_API_KEY
        self.slack_client = WebClient(token=self.api_key)
        # self.logger = logger if logger else utils_init.setup_logger(__name__)  #logging.getLogger(__name__)
        self.testing_flag = testing_flag
        self.testing_dm_or_channel = self.TESTING_CHANNEL


    def make_slack_api_call(self, api_method, **kwargs):
        while True:
            try:
                response = api_method(**kwargs)
                return response
            except SlackApiError as e:
                if e.response["error"] == "ratelimited":
                    delay = int(e.response.headers.get('Retry-After'))
                    time.sleep(delay)
                else:
                    self.print(f"Error making API call: {e}")
                    raise e
    
    def send_dm_or_channel_message(self, channel_or_slack_id, message, thread_ts=None, testing_flag=None):
        """
        Send a message to the given channel or user (by Slack ID) through Direct Message.
        Optionally, reply to a threaded message by providing a thread timestamp.
        """
        channel_or_slack_id = channel_or_slack_id if not testing_flag else self.testing_dm_or_channel

        if channel_or_slack_id.startswith("U"):
            dm = self.make_slack_api_call(self.slack_client.conversations_open, users=channel_or_slack_id)
            channel_or_slack_id = dm['channel']['id']

        response = {}

        if not message:
            logger.warning(f"Message is empty")
            response['ok'] = False
            response['error'] = "ERROR: Tried to send empty message on Slack via slackutils"
        else:
            response = self.make_slack_api_call(
                self.slack_client.chat_postMessage,
                channel=channel_or_slack_id,
                text=message,
                thread_ts=thread_ts,
                unfurl_links=False,
                unfurl_media=False
            )

        return response
    
    def get_list_of_channels(self, bool_public_channels=True, bool_private_channels=True, exclude_archived=True):
        '''https://api.slack.com/methods/conversations.list
            Returns the conversations_list() result of 'all channels
            The object can then be iterated over (for channel in all_channels). Some properties:
            channel_id = channel["id"]
            channel_name = channel["name"]
            status = "private" if channel["is_private"] else "public"
            description = channel["purpose"]["value"]
            topic = channel["topic"]["value"]
            is_archived = channel["is_archived"]
        '''
        public_channels = None
        private_channels = None
        # Get the public channels
        if bool_public_channels:
            response = self.make_slack_api_call(self.slack_client.conversations_list, types="public_channel", exclude_archived=exclude_archived)
            public_channels = response["channels"]

        # Get the private channels
        if bool_private_channels:
            response = self.make_slack_api_call(self.slack_client.conversations_list, types="private_channel", exclude_archived=exclude_archived)
            private_channels = response["channels"]

        all_channels = public_channels + private_channels if public_channels and private_channels else public_channels or private_channels
        
        return all_channels

    def get_channel_messages(self, channel_id, oldest_timestamp=None, newest_timestamp=None):
        """
        Fetch messages from the specified Slack channel.
        Optionally, filter the messages by providing the oldest and/or newest timestamp.
        Handles pagination and rate limits.
        """
        messages = []
        next_cursor = None

        while True:
            # Build kwargs dict based on parameters
            kwargs = {
                "channel": channel_id,
                "inclusive": False,
                "limit": 100,  # Get maximum number of messages per API call
                "cursor": next_cursor,
            }

            # Only add timestamp parameters if they are not None
            if oldest_timestamp:
                kwargs["oldest"] = oldest_timestamp
            if newest_timestamp:
                kwargs["latest"] = newest_timestamp

            # Request the conversation history using make_slack_api_call
            response = self.make_slack_api_call(self.slack_client.conversations_history, **kwargs)
            messages += response.data.get('messages')

            # Check if more messages are available
            next_cursor = response.data.get('response_metadata', {}).get('next_cursor')
            if not next_cursor:
                break

            # Pause before next API call to avoid hitting rate limits (if needed)
            time.sleep(1)

        return messages

  
    def get_channel_members(self, channel_id):
        '''Takes a channel_id string (e.g. "C0921V92") and returns the results of slack_client.conversation_members()'''
        return self.slack_client.conversations_members(channel=channel_id)


    def get_users (self):
        '''return the result of users_list(
                *,
                cursor: str | None = None,
                include_locale: bool | None = None,
                limit: int | None = None,
                team_id: str | None = None,
                **kwargs: Any
            ) -> SlackResponse'''
        return self.make_slack_api_call(self.slack_client.users_list)
        


if __name__ == '__main__':
    slack = SlackConnect()
    channels = slack.get_list_of_channels()
    print (len(channels))