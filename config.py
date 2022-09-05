import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = "5578"
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    HOST = "http://127.0.0.1:"

class cosDB_config:

    """COSMOS db configuration setting """
    uri = "https://localhost:8081"
    key = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="