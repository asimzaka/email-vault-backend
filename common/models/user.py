from dataclasses import dataclass
from rococo.models import VersionedModel


@dataclass
class User(VersionedModel):
    """A User model."""

    first_name: str = None
    last_name: str = None
    company_name: str = None
    email: str = None
    password: str = None
    referral_code: str = None
    is_verified: bool = False
    reset_password_token: str = None
    verification_token: str = None