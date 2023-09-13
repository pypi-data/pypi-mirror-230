import functools

import openapi_client
from openapi_client.apis.tags import (
    access_account_controller_api,
    access_config_controller_api,
    beamline_controller_api,
    dataset_controller_api,
    device_controller_api,
    event_controller_api,
    experiment_account_controller_api,
    experiment_controller_api,
    functional_account_controller_api,
    scan_controller_api,
    session_controller_api,
    user_controller_api,
)
from openapi_client.exceptions import ApiException


class SciBecError(Exception):
    pass


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not args[0].client:
            raise SciBecError("Not logged in.")
        return func(*args, **kwargs)

    return wrapper


class SciBecCore:
    def __init__(self, host: str = "https://bec.development.psi.ch/api/v1") -> None:
        self.client = None
        self.configuration = openapi_client.Configuration(host=host)
        self._access_account = None
        self._access_config = None
        self._beamline = None
        self._dataset = None
        self._device = None
        self._event = None
        self._experiment = None
        self._experiment_account = None
        self._functional_account = None
        self._scan = None
        self._session = None
        self._user = None

    @property
    @login_required
    def access_account(self):
        return self._access_account

    @property
    @login_required
    def access_config(self):
        return self._access_config

    @property
    @login_required
    def beamline(self):
        return self._beamline

    @property
    @login_required
    def dataset(self):
        return self._dataset

    @property
    @login_required
    def device(self):
        return self._device

    @property
    @login_required
    def event(self):
        return self._event

    @property
    @login_required
    def experiment(self):
        return self._experiment

    @property
    @login_required
    def experiment_account(self):
        return self._experiment_account

    @property
    @login_required
    def functional_account(self):
        return self._functional_account

    @property
    @login_required
    def scan(self):
        return self._scan

    @property
    @login_required
    def session(self):
        return self._session

    @property
    @login_required
    def user(self):
        return self._user

    def login(self, username: str = None, password: str = None, token: str = None):
        if not token:
            if not username or not password:
                raise SciBecError("Either username/password or a token have to be specified.")
            client = openapi_client.ApiClient(self.configuration)
            login = user_controller_api.UserControllerLogin(client)
            try:
                res = login.user_controller_login(
                    body={"principal": username, "password": password}
                ).body
                token = res["token"]
            except ApiException:
                raise SciBecError("Failed to login.")
        self.configuration.access_token = token
        self.client = openapi_client.ApiClient(self.configuration)

        self._init_controller()

    def _init_controller(self):
        self._access_account = access_account_controller_api.AccessAccountControllerApi(self.client)
        self._access_config = access_config_controller_api.AccessConfigControllerApi(self.client)
        self._beamline = beamline_controller_api.BeamlineControllerApi(self.client)
        self._dataset = dataset_controller_api.DatasetControllerApi(self.client)
        self._device = device_controller_api.DeviceControllerApi(self.client)
        self._event = event_controller_api.EventControllerApi(self.client)
        self._experiment = experiment_controller_api.ExperimentControllerApi(self.client)
        self._experiment_account = experiment_account_controller_api.ExperimentAccountControllerApi(
            self.client
        )
        self._functional_account = functional_account_controller_api.FunctionalAccountControllerApi(
            self.client
        )
        self._scan = scan_controller_api.ScanControllerApi(self.client)
        self._session = session_controller_api.SessionControllerApi(self.client)
        self._user = user_controller_api.UserControllerApi(self.client)
