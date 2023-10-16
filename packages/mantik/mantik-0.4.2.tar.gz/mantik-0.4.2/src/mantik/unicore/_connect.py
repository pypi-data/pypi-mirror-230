import base64
import logging

import pyunicore.client as pyunicore

import mantik.unicore.exceptions as exceptions

logger = logging.getLogger(__name__)


def create_unicore_api_connection(
    api_url: str,
    user: str,
    password: str,
) -> pyunicore.Client:
    """Create a connection to a cluster of a UNICORE API.

    Parameters
    ----------
    api_url : str
        REST API URL to the cluster's UNICORE server.
    user : str
        JUDOOR user name.
    password : str
        Corresponding JUDOOR user password.

    Raises
    ------
    AuthenticationFailedException
        Authentication on the cluster failed.

    Returns
    -------
    pyunicore.client.Client

    """
    logger.info("Attempting to connect to %s", api_url)
    connection = _connect_to_cluster(
        api_url=api_url,
        user=user,
        password=password,
    )
    if _authentication_failed(connection):
        raise exceptions.AuthenticationFailedException(
            f"Failed to connect to {api_url} -- "
            "check if user and password are correct"
        )
    logger.info("Successfully connected to %s", api_url)
    return connection


def _connect_to_cluster(
    api_url: str,
    user: str,
    password: str,
) -> pyunicore.Client:
    transport = _create_transport(user=user, password=password)
    try:
        client = _create_client(transport=transport, api_url=api_url)
    # In the current version of pyunicore a base Exception is raised
    # when a client is instantiated when the Auth fails.
    # In newer versions it should be possible
    # to catch a pyunicore.credentials.AuthenticationFailedException.
    except Exception:
        raise exceptions.AuthenticationFailedException(
            f"Failed to connect to {api_url} -- "
            "check if user and password are correct"
        )
    logger.debug("Connection properties: %s", client.properties)
    return client


def _create_transport(user: str, password: str) -> pyunicore.Transport:
    logger.debug("Creating transport for user %s", user)
    token = _create_token(user=user, password=password)
    return pyunicore.Transport(credential=token, oidc=False)


def _create_token(user: str, password: str) -> str:
    token = f"{user}:{password}".encode()
    return base64.b64encode(token).decode("ascii")


def _create_client(
    transport: pyunicore.Transport, api_url: str
) -> pyunicore.Client:
    logger.debug("Creating client connection using REST API URL %s", api_url)
    return pyunicore.Client(transport=transport, site_url=api_url)


def _authentication_failed(client: pyunicore.Client) -> bool:
    logger.debug(
        "Connection login information: %s",
        client.properties["client"]["xlogin"],
    )
    return False if client.properties["client"]["xlogin"] else True
