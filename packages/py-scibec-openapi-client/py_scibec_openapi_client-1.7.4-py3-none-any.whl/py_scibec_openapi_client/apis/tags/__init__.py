# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from py_scibec_openapi_client.apis.tag_to_api import tag_to_api

import enum


class TagValues(str, enum.Enum):
    ACCESS_ACCOUNT_CONTROLLER = "AccessAccountController"
    ACCESS_CONFIG_CONTROLLER = "AccessConfigController"
    BEAMLINE_CONTROLLER = "BeamlineController"
    DATASET_CONTROLLER = "DatasetController"
    DEVICE_CONTROLLER = "DeviceController"
    EVENT_CONTROLLER = "EventController"
    EXPERIMENT_ACCOUNT_CONTROLLER = "ExperimentAccountController"
    EXPERIMENT_CONTROLLER = "ExperimentController"
    FUNCTIONAL_ACCOUNT_CONTROLLER = "FunctionalAccountController"
    NXENTITY_CONTROLLER = "NXEntityController"
    OIDCCONTROLLER = "OIDCController"
    SCAN_CONTROLLER = "ScanController"
    SESSION_CONTROLLER = "SessionController"
    USER_CONTROLLER = "UserController"
