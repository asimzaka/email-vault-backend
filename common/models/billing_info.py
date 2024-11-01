from dataclasses import dataclass, field
from rococo.models import VersionedModel


@dataclass
class BillingInfo(VersionedModel):
    """A Billing Info model."""

    user: str = field(default=None, metadata={
        'relationship': {'model': 'User', 'type': 'direct'},
        'field_type': 'record_id'
    })
    name_on_card: str = None
    card_number: str = None
    expiration_date: str = None
    cvv: str = None
