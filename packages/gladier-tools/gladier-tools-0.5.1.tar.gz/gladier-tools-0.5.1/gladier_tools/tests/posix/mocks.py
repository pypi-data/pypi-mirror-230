from typing import List, Mapping, Union
from globus_sdk import AccessTokenAuthorizer, RefreshTokenAuthorizer
from gladier import CallbackLoginManager


def callback(scopes: List[str]) -> Mapping[str, Union[AccessTokenAuthorizer,
                                           RefreshTokenAuthorizer]]:
    return {s: AccessTokenAuthorizer(f'mock_token_{s}') for s in scopes}


MOCK_LOGIN_MANAGER = CallbackLoginManager({}, callback=callback)
