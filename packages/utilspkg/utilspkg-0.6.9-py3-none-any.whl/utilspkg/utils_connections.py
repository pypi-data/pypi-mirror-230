import os
# this file is used to create instances of the classes in the utilspkg folder: DB, Slack, GPT, etc.
from utilspkg import utils_db, utils_slack, utils_gpt


class Connections:
    def __init__(self, testing_flag):
        self.db_connection = utils_db.DBConnect()
        self.slack_connection = utils_slack.SlackConnect(testing_flag=testing_flag)
        self.gpt_connection = utils_gpt.GPTConnect()


# You can create an instance of this class in your main file
connections = None

def initialize_connections(testing_flag=None):
    print("In utils_connections: initialize_connections()")
    global connections
    # if testing_flag is none, check if env variable is set:
    if testing_flag is None:
        testing_flag = os.getenv("TESTING_FLAG") #TESTING_FLAG
    connections = Connections(testing_flag)

def get_connections(testing_flag=None):
    print("In utils_connections: get_connections()")
    global connections
    if connections is None:
        initialize_connections(testing_flag = testing_flag)  
    return connections.db_connection, connections.slack_connection, connections.gpt_connection
