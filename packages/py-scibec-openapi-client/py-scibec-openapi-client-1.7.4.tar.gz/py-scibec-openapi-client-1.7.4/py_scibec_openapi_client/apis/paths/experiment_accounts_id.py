from py_scibec_openapi_client.paths.experiment_accounts_id.get import ApiForget
from py_scibec_openapi_client.paths.experiment_accounts_id.delete import ApiFordelete
from py_scibec_openapi_client.paths.experiment_accounts_id.patch import ApiForpatch


class ExperimentAccountsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
