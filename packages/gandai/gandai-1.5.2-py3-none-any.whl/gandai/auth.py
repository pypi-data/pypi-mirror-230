import os
import random
from dataclasses import asdict, dataclass, field
from hashlib import md5
from time import time

import pandas as pd
from twilio.rest import Client

from gandai.secrets import access_secret_version

# from gandai.models.User import user_exists # create_user

ds = {}
twilio_client = Client(
    access_secret_version("TWILIO_APP"), access_secret_version("TWILIO_TOKEN")
)


@dataclass
class Auth:
    key: str = field(init=False)
    phone: str
    code: str  # 6 digit
    expires: int = field(init=False)
    token: str = field(init=False)

    def __post_init__(self):
        assert len(str(self.code)) == 6
        assert len(str(self.phone)) == 10
        SEVEN_DAYS = 7 * 86400
        self.expires = int(time()) + SEVEN_DAYS
        self.key = f"auth/{self.phone}/{self.expires}"
        self.token = md5(self.key.encode()).hexdigest()


def _send_code(auth: Auth) -> None:
    message = twilio_client.messages.create(
        to=auth.phone,
        from_=access_secret_version("TWILIO_NUMBER"),
        body=f"{auth.code} is your TargetSelect authentication code.",
    )
    print(f"Login Sent to {auth.phone}")


def send_code(phone: str) -> None:
    # Event.create(actor_key=phone)
    auth_code = str(random.randint(100000, 999999))
    auth = Auth(phone=phone, code=auth_code)
    ds[auth.key] = asdict(auth)
    _send_code(auth)


def authenticate(code: str) -> Auth:
    code = code.strip()
    keys = ds.keys()
    df = pd.DataFrame([ds[k] for k in keys])
    df = df[df["expires"] > int(time())]
    df = df[df["code"] == code]
    if len(df) > 0:
        # could parse to Auth and back to dict
        return df.to_dict(orient="records")[0]
    else:
        return None


def validate(token: str) -> bool:
    pass
