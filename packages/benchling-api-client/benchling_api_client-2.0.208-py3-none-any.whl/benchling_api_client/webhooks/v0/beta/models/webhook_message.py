from typing import Union

from ..extensions import UnknownType
from ..models.canvas_initialize_webhook_v0_beta import CanvasInitializeWebhookV0Beta
from ..models.canvas_interaction_webhook_v0_beta import CanvasInteractionWebhookV0Beta
from ..models.lifecycle_activate_webhook_v0_beta import LifecycleActivateWebhookV0Beta
from ..models.lifecycle_deactivate_webhook_v0_beta import LifecycleDeactivateWebhookV0Beta

WebhookMessage = Union[
    CanvasInteractionWebhookV0Beta,
    CanvasInitializeWebhookV0Beta,
    LifecycleActivateWebhookV0Beta,
    LifecycleDeactivateWebhookV0Beta,
    UnknownType,
]
