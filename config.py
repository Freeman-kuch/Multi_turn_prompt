import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = "5578"
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    HOST = "http://127.0.0.1:"