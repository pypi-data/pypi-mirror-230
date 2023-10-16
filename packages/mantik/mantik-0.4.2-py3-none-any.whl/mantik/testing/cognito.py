"""Fakes for testing cognito interactions.

Reference:
https://docs.aws.amazon.com/code-samples/latest/catalog/python-test_tools-cognito_idp_stubber.py.html  # noqa

"""
import dataclasses
import typing as t

import boto3
import botocore.session
import botocore.stub


def patch_boto_client(monkeypatch, json_response):
    def create_fake_client(*args, **kwargs):
        return FakeCognitoClient(json_response)

    monkeypatch.setattr(
        boto3,
        "client",
        create_fake_client,
    )


@dataclasses.dataclass
class FakeCognitoClient:
    json_response: t.Dict
    _client = boto3.client("cognito-idp", region_name="test-region")

    def initiate_auth(
        self, ClientId: str, AuthFlow: str, AuthParameters: t.Dict
    ) -> t.Dict:
        """Fake initiate_auth method and raise error if response is one.

        Notes
        -----
        The boto3.client.exceptions classes take two arguments:
            1. json response (`dict`), which is being parsed by the class.
            2. An `operation_name`, which does not seem to be used
               for the error message.

        """
        if "Error" in self.json_response:
            code = self.json_response["Error"]["Code"]
            if code == "NotAuthorizedException":
                raise self._client.exceptions.NotAuthorizedException(
                    self.json_response, ""
                )
            elif code == "UserNotFoundException":
                raise self._client.exceptions.UserNotFoundException(
                    self.json_response, ""
                )
            raise RuntimeError("Unknown error code in response")
        return self.json_response

    def close(self) -> None:
        pass

    @property
    def exceptions(self):
        return self._client.exceptions


class BotoClientPatcher(botocore.stub.Stubber):
    def __init__(self, client: t.Type[boto3.client], use_stubs: bool = True):
        """
        Initializes the object with a specific client and configures it for
        stubbing or AWS passthrough.

        Parameters
        ----------
        client : boto3.client
            A Boto 3 service client.
        use_stubs : bool, default=True.
            When True, use stubs to intercept requests.
            Otherwise, pass requests through to AWS.
        """
        self.use_stubs = use_stubs
        self.region_name = client.meta.region_name
        self.client = client
        if self.use_stubs:
            super().__init__(client)
        else:
            self.client = client

    @property
    def exceptions(self):
        return self.client.exceptions

    def add_response(self, method: str, service_response, expected_params=None):
        """Add response to a method.

        Parameters
        ----------
        method : str
            Name of the client method to stub.
        service_response : dict
            Response data.
        expected_params: : dict
            A dictionary of the expected parameters to
            be called for the provided service response. The parameters match
            the names of keyword arguments passed to that client call. If
            any of the parameters differ a ``StubResponseError`` is thrown.
            You can use stub.ANY to indicate a particular parameter to ignore
            in validation. stub.ANY is only valid for top level params.

        """

        if self.use_stubs:
            super().add_response(method, service_response, expected_params)

    def add_client_error(
        self,
        method,
        service_error_code="",
        service_message="",
        http_status_code=400,
        service_error_meta=None,
        expected_params=None,
        response_meta=None,
    ):
        """Adds a `ClientError` to the response queue.

        Parameters
        ----------
        method : str
            The name of the service method to return the error on.
        service_error_code : str
            The service error code to return.
            E.g. ``NoSuchBucket``.
        service_message : str
            The service message to return.
            E.g. 'The specified bucket does not exist.'
        http_status_code : int
            The HTTP status code to return
            E.g. 404, etc.
        service_error_meta : dict
            Additional keys to be added to the service error.
        expected_params : dict
            A dictionary of the expected parameters to
            be called for the provided service response. The parameters match
            the names of keyword arguments passed to that client call. If
            any of the parameters differ a ``StubResponseError`` is thrown.
            You can use stub.ANY to indicate a particular parameter to ignore
            in validation.
        response_meta : dict
            Additional keys to be added to the response's ResponseMetadata.
        modeled_fields : dict
            Additional keys to be added to the response based on fields that
            are modeled for the particular error code. These keys will be
            validated against the particular error shape designated by the
            error code.

        """
        if self.use_stubs:
            super().add_client_error(
                method,
                service_error_code,
                service_message,
                http_status_code,
                service_error_meta,
                expected_params,
                response_meta,
            )

    def assert_no_pending_responses(self):
        """When using stubs, verify that no more responses are in the queue."""
        if self.use_stubs:
            super().assert_no_pending_responses()

    def _stub_bifurcator(
        self,
        method: str,
        expected_params: t.Dict = None,
        response: t.Dict = None,
        error_code: str = None,
        error_message: str = None,
    ):
        if expected_params is None:
            expected_params = {}
        if response is None:
            response = {}
        if error_code is None:
            self.add_response(
                method,
                expected_params=expected_params,
                service_response=response,
            )
        else:
            self.add_client_error(
                method,
                expected_params=expected_params,
                service_error_code=error_code,
                service_message=error_message,
            )


class CognitoClientPatcher(BotoClientPatcher):
    def __init__(self, use_stubs: bool = True):
        """Initializes the object with a specific client and configures it for
        patching or AWS passthrough.

        Parameters
        ----------
        use_stubs : bool, default=True.
            When True, use stubs to intercept requests.
            Otherwise, pass requests through to AWS.

        """
        client = botocore.session.get_session().create_client(
            "cognito-idp", region_name="test-region"
        )
        super().__init__(client, use_stubs=use_stubs)

    def patch_initiate_auth_get_token(
        self,
        client_id: str,
        user_name: str,
        password: str,
        secret_hash: str,
        response: t.Dict,
        error_code: str = None,
        error_message: str = None,
    ):
        expected_params = {
            "ClientId": client_id,
            "AuthFlow": "USER_PASSWORD_AUTH",
            "AuthParameters": {
                "USERNAME": user_name,
                "PASSWORD": password,
                "SECRET_HASH": secret_hash,
            },
        }
        self._stub_bifurcator(
            method="initiate_auth",
            expected_params=expected_params,
            response=response,
            error_code=error_code,
            error_message=error_message,
        )

    def patch_initiate_auth_refresh_token(
        self,
        client_id: str,
        refresh_token: str,
        secret_hash: str,
        response: t.Dict,
        error_code: str = None,
        error_message: str = None,
    ):
        expected_params = {
            "ClientId": client_id,
            "AuthFlow": "REFRESH_TOKEN_AUTH",
            "AuthParameters": {
                "REFRESH_TOKEN": refresh_token,
                "SECRET_HASH": secret_hash,
            },
        }
        self._stub_bifurcator(
            method="initiate_auth",
            expected_params=expected_params,
            response=response,
            error_code=error_code,
            error_message=error_message,
        )
