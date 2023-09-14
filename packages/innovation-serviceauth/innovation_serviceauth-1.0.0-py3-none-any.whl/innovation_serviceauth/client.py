import json
from typing import List

from grpc import Channel

from .clients import auth, integrations, mfa
from .constants import *
from .iam import Connection
from .helpers import token
from .helpers.environment import InnovationCredentials


def authenticate(channel: Channel, token: str):
    service = auth.AuthServiceStub(channel)
    auth_token: auth.AuthToken = service.Authenticate(auth.AuthToken(jwt=token))

    return auth_token.jwt

def authorize(channel: Channel, credentials: InnovationCredentials, scope: str):
    resource = scope.split('.')[0]
    admin_scope = f'{resource}.admin'
    scopes: List[str] = [scope, admin_scope, IAM_ADMIN]

    for current_scope in scopes:
        jwtoken = token.generate(credentials, current_scope)
        authenticated = authenticate(channel, jwtoken)

        if authenticated != "":
            return True

    return False

class MFA:
    def generate_otp(client_secret: str) -> str:
        with Connection() as (channel, credentials):
            if not authorize(channel, credentials, MFA_GENERATE):
                return Exception(ERR_NOT_ALLOWED)

            mfa_service = mfa.MFAServiceStub(channel)
            generate_otp_request = mfa.GenerateOTPTokenRequest(
                principal=credentials.principal,
                client_secret=client_secret
            )

            otp = mfa_service.GenerateOTPToken(generate_otp_request).token
            return otp

    def validate_otp(token: str, client_secret: str) -> bool:
        with Connection() as (channel, credentials):
            if not authorize(channel, credentials, MFA_VALIDATE):
                return Exception(ERR_NOT_ALLOWED)

            mfa_service = mfa.MFAServiceStub(channel)
            validate_otp_request = mfa.ValidateOTPTokenRequest(
                token=token,
                principal=credentials.principal,
                client_secret=client_secret
            )

            is_valid = mfa_service.ValidateOTPToken(validate_otp_request).is_valid
            return is_valid

class Integrations:
    def generate_jwt(headers: dict, claims: dict, private_key: str) -> str:
        with Connection() as (channel, credentials):
            if not authorize(channel, credentials, TOKEN_GENERATE):
                return Exception(ERR_NOT_ALLOWED)

            headers = json.dumps(headers)
            claims = json.dumps(claims)

            integration_service = integrations.IntegrationsServiceStub(channel)
            generate_jwt_request = integrations.GenerateJWTRequest(
                header=headers,
                claims=claims,
                private_key=private_key
            )

            token = integration_service.GenerateJWT(generate_jwt_request).jwt
            return token

    def validate_jwt(token: str, private_key: str) -> str:
        with Connection() as (channel, credentials):
            if not authorize(channel, credentials, TOKEN_VALIDATE):
                return Exception(ERR_NOT_ALLOWED)

            integration_service = integrations.IntegrationsServiceStub(channel)
            validate_jwt_request = integrations.ValidateJWTRequest(
                jwt=token,
                private_key=private_key
            )

            token = integration_service.ValidateJWT(validate_jwt_request).jwt
            return token

class Client:
    def __init__(self):
        self.mfa_service = MFA
        self.integrations = Integrations


def new_client():
    with Connection() as (channel, credentials):
        if not authorize(channel, credentials, AUTH_CONNECT):
            return Exception(ERR_NOT_ALLOWED)

    return Client()