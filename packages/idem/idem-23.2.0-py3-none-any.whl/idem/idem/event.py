import json
from datetime import datetime
from typing import Any
from typing import Dict


async def put(
    hub,
    body: Any,
    profile: str = "default",
    tags: Dict[str, Any] = None,
):
    # Sending async event by putting it on the evbus broker queue
    if tags is None:
        tags = {}
    date = datetime.now().strftime("%H:%M:%S:%f")
    hub.log.debug(f"{date}: Event put: run_name='{hub.idem.RUN_NAME}' tags='{tags}'")
    await hub.evbus.broker.put(
        profile=profile, body=dict(tags=tags, message=body, run_name=hub.idem.RUN_NAME)
    )


def put_nowait(
    hub,
    body: Any,
    profile: str = "default",
    tags: Dict[str, Any] = None,
):
    # Sending sync event
    if tags is None:
        tags = {}

    hub.evbus.broker.put_nowait(
        profile=profile, body=dict(tags=tags, message=body, run_name=hub.idem.RUN_NAME)
    )


async def publish_error_callback_handler(hub, error_data: dict):
    """
    A default idem callback handler for publish event failure which pushes an error event back to the queue

    .. code-block:: json

        {
            "tags": {
                "plugin": "<plugin-name>",
                <original-event-tags>
            },
            "publish_event_error_message": "<error-message-from-publish-failure>",
            "run_name": "<run-name>"
        }

    """
    if error_data:
        original_body = json.loads(error_data["body"].decode())
        new_tags = {
            "ref": "idem.event.publish_error_callback_handler",
            "plugin": error_data.get("plugin", None),
        }
        run_name = ""
        if original_body:
            if original_body.get("publish_event_error_message"):
                # If this event failed to publish error event, return it.
                # The error would be logged already with evbus
                return

            original_tags = original_body.get("tags", {})
            new_tags = original_tags | new_tags
            run_name = original_body.get("run_name", None)

        await hub.evbus.broker.put(
            profile=error_data["profile"],
            body=dict(
                tags=new_tags,
                run_name=run_name,
                publish_event_error_message=str(error_data["exception"]),
            ),
        )
