import json
import os
import requests

from .exceptions import (
    AuthenticationFailedError,
    DuplicateDocumentContentError,
    DuplicateKnowledgeBaseError,
    DocumentLengthError,
    InternalServerError,
    InvalidRequestError,
    NotFoundError,
)


_BASE_URL = 'https://api.superpowered.ai/v1'
API_KEY_PAIR = (None, None)


def _set_api_key(key_id: str, key_secret: str):
    global API_KEY_PAIR
    API_KEY_PAIR = (key_id, key_secret)


def get_base_url():
    return _BASE_URL


def _set_base_url(base_url: str):
    global _BASE_URL
    _BASE_URL = base_url


def auth():
    # default to use the API_KEY_PAIR if set
    if API_KEY_PAIR[0] and API_KEY_PAIR[1]:
        return API_KEY_PAIR

    # otherwise, use the environment variables
    if not os.getenv('SUPERPOWERED_API_KEY_ID') or not os.getenv('SUPERPOWERED_API_KEY_SECRET'):
        raise Exception('SUPERPOWERED_API_KEY_ID and SUPERPOWERED_API_KEY_SECRET must be set as environment variables')
    return (os.getenv('SUPERPOWERED_API_KEY_ID'), os.getenv('SUPERPOWERED_API_KEY_SECRET'))


################## ERROR HANDLING ##################
def read_errors():
    module_path = os.path.abspath(__file__)
    module_dir = os.path.dirname(module_path)
    errors_path = os.path.join(module_dir, 'errors.json')
    
    with open(errors_path) as file:
        errors_data = json.load(file)
    
    return errors_data


ERRORS = {e['code']: e for e in read_errors()}


def create_exception_class(exception_name: str):
    return type(exception_name, (Exception,), {})


def make_api_call(args: dict) -> dict:
    exception_classes = {
        "AuthenticationFailedError": AuthenticationFailedError,
        "DuplicateDocumentContentError": DuplicateDocumentContentError,
        "DocumentLengthError": DocumentLengthError,
        "InternalServerError": InternalServerError,
        "InvalidRequestError": InvalidRequestError,
        "NotFoundError": NotFoundError,
        "TimeoutError": TimeoutError,
        "DuplicateKnowledgeBaseError": DuplicateKnowledgeBaseError
    }

    resp = requests.request(**args)
    headers = resp.headers
    if args['method'] == 'DELETE':
        return resp.ok
    resp_json = resp.json()
    if headers.get('error_code'):
        error_code = int(headers['error_code'])
        if error_code in ERRORS:
            try:
                _exp = exception_classes[ERRORS[error_code]['python_sdk_exception']]
                raise _exp(resp_json, resp.status_code)
            except KeyError:
                raise Exception(resp_json, resp.status_code)
        else:
            raise Exception(resp_json, resp.status_code)
    elif not resp.ok:
        raise Exception(resp_json, resp.status_code)
    else:
        return resp_json

