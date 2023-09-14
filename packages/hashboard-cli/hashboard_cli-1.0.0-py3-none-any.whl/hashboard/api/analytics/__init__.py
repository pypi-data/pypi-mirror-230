from typing import Optional
import requests

from hashboard.constants import HASHBOARD_BASE_URI


def track(event: str, value: dict, duration: Optional[int] = None):
    """Send an analytics event to the app server.

    Args:
        event (str): Event name.
        value (dict): Dict including information about the event.
        duration (Optional[int], optional): Duration of the event in seconds. Defaults to None.
    """
    try:
        requests.post(
            f"{HASHBOARD_BASE_URI}/services/analytics/cli_track",
            headers={},
            json={
                "event": event,
                "value": value,
                "duration": duration,
            },
            timeout=0.5,
        )
    except:
        pass
