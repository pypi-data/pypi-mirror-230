import typing_extensions

from py-scibec-openapi-client.apis.tags import TagValues
from py-scibec-openapi-client.apis.tags.access_account_controller_api import AccessAccountControllerApi
from py-scibec-openapi-client.apis.tags.access_config_controller_api import AccessConfigControllerApi
from py-scibec-openapi-client.apis.tags.beamline_controller_api import BeamlineControllerApi
from py-scibec-openapi-client.apis.tags.dataset_controller_api import DatasetControllerApi
from py-scibec-openapi-client.apis.tags.device_controller_api import DeviceControllerApi
from py-scibec-openapi-client.apis.tags.event_controller_api import EventControllerApi
from py-scibec-openapi-client.apis.tags.experiment_account_controller_api import ExperimentAccountControllerApi
from py-scibec-openapi-client.apis.tags.experiment_controller_api import ExperimentControllerApi
from py-scibec-openapi-client.apis.tags.functional_account_controller_api import FunctionalAccountControllerApi
from py-scibec-openapi-client.apis.tags.nx_entity_controller_api import NXEntityControllerApi
from py-scibec-openapi-client.apis.tags.oidc_controller_api import OIDCControllerApi
from py-scibec-openapi-client.apis.tags.scan_controller_api import ScanControllerApi
from py-scibec-openapi-client.apis.tags.session_controller_api import SessionControllerApi
from py-scibec-openapi-client.apis.tags.user_controller_api import UserControllerApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.ACCESS_ACCOUNT_CONTROLLER: AccessAccountControllerApi,
        TagValues.ACCESS_CONFIG_CONTROLLER: AccessConfigControllerApi,
        TagValues.BEAMLINE_CONTROLLER: BeamlineControllerApi,
        TagValues.DATASET_CONTROLLER: DatasetControllerApi,
        TagValues.DEVICE_CONTROLLER: DeviceControllerApi,
        TagValues.EVENT_CONTROLLER: EventControllerApi,
        TagValues.EXPERIMENT_ACCOUNT_CONTROLLER: ExperimentAccountControllerApi,
        TagValues.EXPERIMENT_CONTROLLER: ExperimentControllerApi,
        TagValues.FUNCTIONAL_ACCOUNT_CONTROLLER: FunctionalAccountControllerApi,
        TagValues.NXENTITY_CONTROLLER: NXEntityControllerApi,
        TagValues.OIDCCONTROLLER: OIDCControllerApi,
        TagValues.SCAN_CONTROLLER: ScanControllerApi,
        TagValues.SESSION_CONTROLLER: SessionControllerApi,
        TagValues.USER_CONTROLLER: UserControllerApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.ACCESS_ACCOUNT_CONTROLLER: AccessAccountControllerApi,
        TagValues.ACCESS_CONFIG_CONTROLLER: AccessConfigControllerApi,
        TagValues.BEAMLINE_CONTROLLER: BeamlineControllerApi,
        TagValues.DATASET_CONTROLLER: DatasetControllerApi,
        TagValues.DEVICE_CONTROLLER: DeviceControllerApi,
        TagValues.EVENT_CONTROLLER: EventControllerApi,
        TagValues.EXPERIMENT_ACCOUNT_CONTROLLER: ExperimentAccountControllerApi,
        TagValues.EXPERIMENT_CONTROLLER: ExperimentControllerApi,
        TagValues.FUNCTIONAL_ACCOUNT_CONTROLLER: FunctionalAccountControllerApi,
        TagValues.NXENTITY_CONTROLLER: NXEntityControllerApi,
        TagValues.OIDCCONTROLLER: OIDCControllerApi,
        TagValues.SCAN_CONTROLLER: ScanControllerApi,
        TagValues.SESSION_CONTROLLER: SessionControllerApi,
        TagValues.USER_CONTROLLER: UserControllerApi,
    }
)
