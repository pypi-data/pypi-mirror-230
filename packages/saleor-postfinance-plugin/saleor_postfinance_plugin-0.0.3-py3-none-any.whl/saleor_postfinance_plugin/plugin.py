from typing import TYPE_CHECKING

from saleor.payment.gateways.utils import get_supported_currencies, require_active_plugin
from saleor.plugins.base_plugin import BasePlugin, ConfigurationTypeField

from . import GatewayConfig, confirm, process_payment

GATEWAY_NAME = "PostFinance"

if TYPE_CHECKING:
    from . import GatewayResponse, PaymentData


class PostFinanceGatewayPlugin(BasePlugin):
    PLUGIN_NAME = GATEWAY_NAME
    PLUGIN_ID = "significa.payments.postfinance"
    DEFAULT_CONFIGURATION = [
        {"name": "Supported currencies", "value": "CHF"},
        {"name": "Space ID", "value": None},
        {"name": "User ID", "value": None},
        {"name": "User Secret Key", "value": None},
    ]
    CONFIG_STRUCTURE = {
        "Space ID": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "PostFinance Space ID",
            "label": "Space ID",
        },
        "User ID": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "PostFinance Application User ID",
            "label": "User ID",
        },
        "User Secret Key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "PostFinance Application User Secret Key",
            "label": "Secret Key",
        },
        "Supported currencies": {
            "type": ConfigurationTypeField.STRING,
            "help_text": (
                "Determines currencies supported by gateway."
                " Please enter currency codes separated by a comma."
            ),
            "label": "Supported currencies",
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configuration = {
            item["name"]: item["value"]
            for item in self.configuration
        }

        self.config = GatewayConfig(
            gateway_name=GATEWAY_NAME,
            auto_capture=None,
            supported_currencies=configuration["Supported currencies"],
            connection_params={
                "space_id": (
                    int(configuration["Space ID"])
                    if configuration["Space ID"]
                    else None
                ),
                "user_id": (
                    int(configuration["User ID"])
                    if configuration["User ID"]
                    else None
                ),
                "user_secret": configuration["User Secret Key"],
            }
        )

    def _get_gateway_config(self):
        return self.config

    @require_active_plugin
    def token_is_required_as_payment_input(self, previous_value):
        return False

    @require_active_plugin
    def confirm_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return confirm(payment_information, self._get_gateway_config())

    @require_active_plugin
    def process_payment(
        self, payment_information: "PaymentData", previous_value
    ) -> "GatewayResponse":
        return process_payment(payment_information, self._get_gateway_config())

    @require_active_plugin
    def get_supported_currencies(self, previous_value):
        config = self._get_gateway_config()
        return get_supported_currencies(config, GATEWAY_NAME)
