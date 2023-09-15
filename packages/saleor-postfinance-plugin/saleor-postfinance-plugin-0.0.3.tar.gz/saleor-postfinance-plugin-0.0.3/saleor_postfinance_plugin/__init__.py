from typing import Optional

from postfinancecheckout import (
    Configuration, LineItem, LineItemType, Transaction, TransactionPaymentPageServiceApi,
    TransactionServiceApi, TransactionState,
)
from saleor.payment import TransactionKind
from saleor.payment.interface import GatewayConfig, GatewayResponse, PaymentData

POSTFINANCE_E_FINANCE_ID = 1461146715166
POSTFINANCE_CARD_ID = 1461144402291


def capture(
    payment_information: PaymentData,
    config: GatewayConfig
) -> GatewayResponse:
    success_url = payment_information.data["successUrl"]
    fail_url = payment_information.data["failUrl"]

    line_item = LineItem(
        name="Order",
        quantity=1,
        amount_including_tax=float(payment_information.amount),
        type=LineItemType.PRODUCT,
        unique_id=str(payment_information.payment_id),
    )

    transaction = Transaction(
        allowed_payment_method_brands=[
            POSTFINANCE_E_FINANCE_ID,
            POSTFINANCE_CARD_ID,
        ],
        currency=payment_information.currency,
        success_url=success_url,
        failed_url=fail_url,
        line_items=[line_item],
    )

    space_id = _get_space_id(config=config)
    postfinance_transaction_service = _get_transaction_service(config=config)
    postfinance_transaction_payment_page_service = (
        _get_transaction_payment_page_service(
            config=config
        )
    )

    postfinance_transaction = postfinance_transaction_service.create(
        space_id=space_id,
        transaction=transaction,
    )

    payment_page_url = (
        postfinance_transaction_payment_page_service.payment_page_url(
            space_id=space_id,
            id=postfinance_transaction.id,
        )
    )

    return GatewayResponse(
        transaction_id=postfinance_transaction.id,
        is_success=True,
        action_required=True,
        action_required_data={
            "payment_page_url": payment_page_url
        },
        kind=TransactionKind.ACTION_TO_CONFIRM,
        currency=payment_information.currency,
        amount=payment_information.amount,
        error=None,
    )


def confirm(
    payment_information: PaymentData,
    config: GatewayConfig
) -> GatewayResponse:
    error: Optional[str]
    error = "Unable to process capture"
    success = False

    postfinance_transaction_id = int(payment_information.token)
    space_id = _get_space_id(config=config)

    postfinance_transaction_service = _get_transaction_service(config=config)
    postfinance_transaction = postfinance_transaction_service.read(
        space_id=space_id,
        id=postfinance_transaction_id
    )

    if postfinance_transaction.state in (
        TransactionState.FULFILL,
        TransactionState.AUTHORIZED
    ):
        success = True
        error = None

    return GatewayResponse(
        transaction_id=postfinance_transaction_id,
        is_success=success,
        action_required=False,
        kind=TransactionKind.CAPTURE,
        amount=payment_information.amount,
        currency=payment_information.currency,
        error=error,
    )


def process_payment(
    payment_information: PaymentData, config: GatewayConfig
) -> GatewayResponse:
    return capture(payment_information, config)


def _get_transaction_service(config: GatewayConfig):
    return TransactionServiceApi(
        configuration=_get_configuration(**config.connection_params)
    )


def _get_transaction_payment_page_service(config: GatewayConfig):
    return TransactionPaymentPageServiceApi(
        configuration=_get_configuration(**config.connection_params)
    )


def _get_space_id(config: GatewayConfig):
    return config.connection_params.get("space_id")


def _get_configuration(user_id: str, user_secret: str, **_kwargs):
    return Configuration(
        user_id=user_id,
        api_secret=user_secret
    )
