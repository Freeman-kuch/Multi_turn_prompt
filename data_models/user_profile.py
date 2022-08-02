
from botbuilder.schema import Attachment  # an attachment within an activity


class UserProfile:
    """
      This is our application state. Just a regular serializable Python class. That is to say this is the Bot memory
    """

    def __init__(self, name: str = "Anonymous", product_type: str = None, price_to_negotiate: int = 0,
                 picture_of_item: Attachment = None, purpose_of_negotiation: str = None):
        self.name = name
        self.product_type = product_type
        self.purpose_of_negotiation = purpose_of_negotiation
        self.price_to_negotiate = price_to_negotiate
        self.picture_of_item = picture_of_item
