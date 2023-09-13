import typing_extensions

from py-scibec-openapi-client.paths import PathValues
from py-scibec-openapi-client.apis.paths.access_accounts_count import AccessAccountsCount
from py-scibec-openapi-client.apis.paths.access_accounts_id import AccessAccountsId
from py-scibec-openapi-client.apis.paths.access_accounts import AccessAccounts
from py-scibec-openapi-client.apis.paths.access_configs_count import AccessConfigsCount
from py-scibec-openapi-client.apis.paths.access_configs_id import AccessConfigsId
from py-scibec-openapi-client.apis.paths.access_configs import AccessConfigs
from py-scibec-openapi-client.apis.paths.auth_callback import AuthCallback
from py-scibec-openapi-client.apis.paths.auth_login import AuthLogin
from py-scibec-openapi-client.apis.paths.auth_logout import AuthLogout
from py-scibec-openapi-client.apis.paths.beamlines_count import BeamlinesCount
from py-scibec-openapi-client.apis.paths.beamlines_id import BeamlinesId
from py-scibec-openapi-client.apis.paths.beamlines import Beamlines
from py-scibec-openapi-client.apis.paths.datasets_count import DatasetsCount
from py-scibec-openapi-client.apis.paths.datasets_id import DatasetsId
from py-scibec-openapi-client.apis.paths.datasets import Datasets
from py-scibec-openapi-client.apis.paths.devices_count import DevicesCount
from py-scibec-openapi-client.apis.paths.devices_id import DevicesId
from py-scibec-openapi-client.apis.paths.devices import Devices
from py-scibec-openapi-client.apis.paths.events_count import EventsCount
from py-scibec-openapi-client.apis.paths.events_id import EventsId
from py-scibec-openapi-client.apis.paths.events import Events
from py-scibec-openapi-client.apis.paths.experiment_accounts_count import ExperimentAccountsCount
from py-scibec-openapi-client.apis.paths.experiment_accounts_id import ExperimentAccountsId
from py-scibec-openapi-client.apis.paths.experiment_accounts import ExperimentAccounts
from py-scibec-openapi-client.apis.paths.experiments_count import ExperimentsCount
from py-scibec-openapi-client.apis.paths.experiments_id import ExperimentsId
from py-scibec-openapi-client.apis.paths.experiments import Experiments
from py-scibec-openapi-client.apis.paths.functional_accounts_count import FunctionalAccountsCount
from py-scibec-openapi-client.apis.paths.functional_accounts_id import FunctionalAccountsId
from py-scibec-openapi-client.apis.paths.functional_accounts import FunctionalAccounts
from py-scibec-openapi-client.apis.paths.nxentities_count import NxentitiesCount
from py-scibec-openapi-client.apis.paths.nxentities_entry import NxentitiesEntry
from py-scibec-openapi-client.apis.paths.nxentities_id import NxentitiesId
from py-scibec-openapi-client.apis.paths.nxentities import Nxentities
from py-scibec-openapi-client.apis.paths.scans_count import ScansCount
from py-scibec-openapi-client.apis.paths.scans_id import ScansId
from py-scibec-openapi-client.apis.paths.scans import Scans
from py-scibec-openapi-client.apis.paths.sessions_count import SessionsCount
from py-scibec-openapi-client.apis.paths.sessions_id import SessionsId
from py-scibec-openapi-client.apis.paths.sessions import Sessions
from py-scibec-openapi-client.apis.paths.users_login import UsersLogin
from py-scibec-openapi-client.apis.paths.users_me import UsersMe
from py-scibec-openapi-client.apis.paths.users_user_id import UsersUserId
from py-scibec-openapi-client.apis.paths.users import Users

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.ACCESSACCOUNTS_COUNT: AccessAccountsCount,
        PathValues.ACCESSACCOUNTS_ID: AccessAccountsId,
        PathValues.ACCESSACCOUNTS: AccessAccounts,
        PathValues.ACCESSCONFIGS_COUNT: AccessConfigsCount,
        PathValues.ACCESSCONFIGS_ID: AccessConfigsId,
        PathValues.ACCESSCONFIGS: AccessConfigs,
        PathValues.AUTH_CALLBACK: AuthCallback,
        PathValues.AUTH_LOGIN: AuthLogin,
        PathValues.AUTH_LOGOUT: AuthLogout,
        PathValues.BEAMLINES_COUNT: BeamlinesCount,
        PathValues.BEAMLINES_ID: BeamlinesId,
        PathValues.BEAMLINES: Beamlines,
        PathValues.DATASETS_COUNT: DatasetsCount,
        PathValues.DATASETS_ID: DatasetsId,
        PathValues.DATASETS: Datasets,
        PathValues.DEVICES_COUNT: DevicesCount,
        PathValues.DEVICES_ID: DevicesId,
        PathValues.DEVICES: Devices,
        PathValues.EVENTS_COUNT: EventsCount,
        PathValues.EVENTS_ID: EventsId,
        PathValues.EVENTS: Events,
        PathValues.EXPERIMENTACCOUNTS_COUNT: ExperimentAccountsCount,
        PathValues.EXPERIMENTACCOUNTS_ID: ExperimentAccountsId,
        PathValues.EXPERIMENTACCOUNTS: ExperimentAccounts,
        PathValues.EXPERIMENTS_COUNT: ExperimentsCount,
        PathValues.EXPERIMENTS_ID: ExperimentsId,
        PathValues.EXPERIMENTS: Experiments,
        PathValues.FUNCTIONALACCOUNTS_COUNT: FunctionalAccountsCount,
        PathValues.FUNCTIONALACCOUNTS_ID: FunctionalAccountsId,
        PathValues.FUNCTIONALACCOUNTS: FunctionalAccounts,
        PathValues.NXENTITIES_COUNT: NxentitiesCount,
        PathValues.NXENTITIES_ENTRY: NxentitiesEntry,
        PathValues.NXENTITIES_ID: NxentitiesId,
        PathValues.NXENTITIES: Nxentities,
        PathValues.SCANS_COUNT: ScansCount,
        PathValues.SCANS_ID: ScansId,
        PathValues.SCANS: Scans,
        PathValues.SESSIONS_COUNT: SessionsCount,
        PathValues.SESSIONS_ID: SessionsId,
        PathValues.SESSIONS: Sessions,
        PathValues.USERS_LOGIN: UsersLogin,
        PathValues.USERS_ME: UsersMe,
        PathValues.USERS_USER_ID: UsersUserId,
        PathValues.USERS: Users,
    }
)

path_to_api = PathToApi(
    {
        PathValues.ACCESSACCOUNTS_COUNT: AccessAccountsCount,
        PathValues.ACCESSACCOUNTS_ID: AccessAccountsId,
        PathValues.ACCESSACCOUNTS: AccessAccounts,
        PathValues.ACCESSCONFIGS_COUNT: AccessConfigsCount,
        PathValues.ACCESSCONFIGS_ID: AccessConfigsId,
        PathValues.ACCESSCONFIGS: AccessConfigs,
        PathValues.AUTH_CALLBACK: AuthCallback,
        PathValues.AUTH_LOGIN: AuthLogin,
        PathValues.AUTH_LOGOUT: AuthLogout,
        PathValues.BEAMLINES_COUNT: BeamlinesCount,
        PathValues.BEAMLINES_ID: BeamlinesId,
        PathValues.BEAMLINES: Beamlines,
        PathValues.DATASETS_COUNT: DatasetsCount,
        PathValues.DATASETS_ID: DatasetsId,
        PathValues.DATASETS: Datasets,
        PathValues.DEVICES_COUNT: DevicesCount,
        PathValues.DEVICES_ID: DevicesId,
        PathValues.DEVICES: Devices,
        PathValues.EVENTS_COUNT: EventsCount,
        PathValues.EVENTS_ID: EventsId,
        PathValues.EVENTS: Events,
        PathValues.EXPERIMENTACCOUNTS_COUNT: ExperimentAccountsCount,
        PathValues.EXPERIMENTACCOUNTS_ID: ExperimentAccountsId,
        PathValues.EXPERIMENTACCOUNTS: ExperimentAccounts,
        PathValues.EXPERIMENTS_COUNT: ExperimentsCount,
        PathValues.EXPERIMENTS_ID: ExperimentsId,
        PathValues.EXPERIMENTS: Experiments,
        PathValues.FUNCTIONALACCOUNTS_COUNT: FunctionalAccountsCount,
        PathValues.FUNCTIONALACCOUNTS_ID: FunctionalAccountsId,
        PathValues.FUNCTIONALACCOUNTS: FunctionalAccounts,
        PathValues.NXENTITIES_COUNT: NxentitiesCount,
        PathValues.NXENTITIES_ENTRY: NxentitiesEntry,
        PathValues.NXENTITIES_ID: NxentitiesId,
        PathValues.NXENTITIES: Nxentities,
        PathValues.SCANS_COUNT: ScansCount,
        PathValues.SCANS_ID: ScansId,
        PathValues.SCANS: Scans,
        PathValues.SESSIONS_COUNT: SessionsCount,
        PathValues.SESSIONS_ID: SessionsId,
        PathValues.SESSIONS: Sessions,
        PathValues.USERS_LOGIN: UsersLogin,
        PathValues.USERS_ME: UsersMe,
        PathValues.USERS_USER_ID: UsersUserId,
        PathValues.USERS: Users,
    }
)
