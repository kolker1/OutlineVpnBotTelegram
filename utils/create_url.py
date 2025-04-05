from typing import Literal

from pydantic import BaseModel
from yarl import URL

from config.loading import config


class Payment(BaseModel):
    sum: Literal[50, 100, 250, 500]

    @property
    def create_url(self):
        base_url = 'https://yoomoney.ru/quickpay/confirm.xml'
        params = {
            'receiver': config.CARD.get_secret_value(),
            'quickpay-form': 'shop',
            'targets': 'Sponsor this project',
            'paymentType': 'SB',
            'sum': self.sum
        }
        url_with_params = str(URL(base_url).with_query(params))
        return url_with_params
