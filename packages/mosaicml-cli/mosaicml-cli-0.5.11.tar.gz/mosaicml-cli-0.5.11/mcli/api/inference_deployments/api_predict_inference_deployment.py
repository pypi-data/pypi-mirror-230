""" Predict on an Inference Deployment """
from __future__ import annotations

from http import HTTPStatus
from typing import Any, Callable, Dict, Optional, Union, cast

import requests
import validators
from requests import Response

from mcli import config
from mcli.api.exceptions import InferenceServerException, MAPIException
from mcli.api.inference_deployments import get_inference_deployments
from mcli.api.model.inference_deployment import InferenceDeployment

__all__ = ['predict']


def predict(
    deployment: Union[InferenceDeployment, str],
    inputs: Dict[str, Any],
    *,
    timeout: Optional[int] = 60,
) -> Dict[str, Any]:
    """Sends input to \'/predict\' endpoint of an inference deployment on the MosaicML
    platform. Runs prediction on input and returns output produced by the model.

    Arguments:
        deployment: The deployment to make a prediction with. Can be a InferenceDeployment object,
            the name of an deployment, or a string which is of the form https://<deployment dns>.
        input: Input data to run prediction on in the form of dictionary
        timeout: Time, in seconds, in which the call should complete. If the call
            takes too long, a TimeoutError will be raised.
    Raises:
        HTTPError: If sending the request to the endpoint fails
        MAPIException: If connecting to MAPI, raised when a MAPI communication error occurs
    """
    validate_url = cast(Callable[[str], bool], validators.url)
    if isinstance(deployment, str) and not validate_url(deployment):
        # if a string is passed in that is not a url then lookup the deployment and get the name
        deployment_objs = get_inference_deployments(deployments=[deployment])
        if len(deployment_objs) == 0:
            raise MAPIException(HTTPStatus.NOT_FOUND, f'No inference deployment found with name {deployment}.')
        deployment = deployment_objs[0]
    conf = config.MCLIConfig.load_config()
    api_key = conf.api_key
    headers = {
        'authorization': api_key,
    }
    base_url = deployment
    if isinstance(deployment, InferenceDeployment):
        base_url = f'https://{deployment.public_dns}'
    try:
        resp: Response = requests.post(url=f'{base_url}/predict', timeout=timeout, json=inputs, headers=headers)
        if resp.ok:
            try:
                return resp.json()
            except requests.JSONDecodeError as e:
                raise InferenceServerException.from_bad_response(resp) from e
        else:
            raise InferenceServerException.from_server_error_response(resp.content.decode().strip(), resp.status_code)
    except requests.exceptions.ReadTimeout as e:
        raise InferenceServerException.from_server_error_response(str(e), HTTPStatus.REQUEST_TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        raise InferenceServerException.from_requests_error(e) from e
