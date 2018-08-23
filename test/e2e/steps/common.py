import json
from functools import partial
from typing import Optional, Mapping, Any

from flask.testing import FlaskClient


def make_request(
    client:     FlaskClient, endpoint: str, method: str,
    parameters: Optional[str] = None,
    data:       Optional[Mapping[str, Any]] = None
) -> Any:
    if parameters is not None:
        parameters = '&'.join(parameters.split(','))
        endpoint = '?'.join([endpoint, parameters])
    method = partial(getattr(client, method.lower()), endpoint)
    if data is not None:
        return method(data=json.dumps(data), content_type='application/json')
    return method()
