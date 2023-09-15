from dataclasses import dataclass

import httplib2
from googleapiclient.discovery import Resource, build
from oauth2client.service_account import ServiceAccountCredentials


@dataclass
class GoogleService:
    version: str
    service_name: str
    scope: str


@dataclass
class GoogleKeys:
    type: str
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_x509_cert_url: str


def get_google_service(
    google_keys: dict[str, str], scope: list[str] | str, service_name: str, version: str
) -> Resource:
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        keyfile_dict=google_keys,
        scopes=scope,
    )
    http_auth = credentials.authorize(httplib2.Http())
    return build(serviceName=service_name, version=version, http=http_auth)
