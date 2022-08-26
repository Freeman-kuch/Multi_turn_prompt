
from botbuilder.schema import Attachment


class UserProfile:
    """
      This is our application state. Just a regular serializable Python class."""
    id = 0

    def __init__(self, name: str = "Anonymous", product_type: str = None, price_to_negotiate: int = 0,
                 picture_of_item: Attachment = None, purpose_of_negotiation: str = None):
        self.id += 1
        self.name = name
        self.product_type = product_type
        self.purpose_of_negotiation = purpose_of_negotiation
        self.price_to_negotiate = price_to_negotiate
        self.picture_of_item = picture_of_item
