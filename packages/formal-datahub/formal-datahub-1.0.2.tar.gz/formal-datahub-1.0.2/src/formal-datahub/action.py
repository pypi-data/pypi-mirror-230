import base64
import hashlib
import hmac

import backoff

from datahub_actions.action.action import Action
from datahub_actions.event.event_envelope import EventEnvelope
from datahub_actions.pipeline.pipeline_context import PipelineContext

import requests

from pydantic.fields import Field

from datahub.configuration.common import ConfigModel


class FormalSourceConfig(ConfigModel):
    webhook_secret: str = Field(description="Webhook secret")
    org_id: str = Field(description="Organization Id")


class FormalAction(Action):
    config: FormalSourceConfig

    @classmethod
    def create(cls, config_dict: dict, ctx: PipelineContext) -> "Action":
        config = FormalSourceConfig.parse_obj(config_dict)
        return cls(config, ctx)

    def __init__(self, config, ctx: PipelineContext):
        self.ctx = ctx
        self.config = config

    @staticmethod
    def sign_request(key, message):
        message = bytes(message, 'utf-8')
        key = bytes(key, 'utf-8')

        digester = hmac.new(key, message, hashlib.sha256)
        signature1 = digester.digest()

        signature2 = base64.b64encode(signature1)

        signature = signature2.decode('utf-8')
        return signature

    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10,
                          giveup=lambda e: e.response is not None and 400 <= e.response.status_code < 500,
                          jitter=backoff.full_jitter)
    def perform_request(self, url, data, headers):
        return requests.post(url, data=data, headers=headers)

    def act(self, event: EventEnvelope) -> None:
        base_url = "https://api.formalcloud.net/webhook/datahub"
        json_data = event.as_json()
        signature = self.sign_request(self.config.webhook_secret, json_data)

        headers = {
            'Formal-Signature': signature,
            'Formal-Organization': self.config.org_id
        }

        self.perform_request(base_url, data=json_data, headers=headers)

    def close(self) -> None:
        pass
