from py_scibec_openapi_client.paths.functional_accounts_id.get import ApiForget
from py_scibec_openapi_client.paths.functional_accounts_id.delete import ApiFordelete
from py_scibec_openapi_client.paths.functional_accounts_id.patch import ApiForpatch


class FunctionalAccountsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
