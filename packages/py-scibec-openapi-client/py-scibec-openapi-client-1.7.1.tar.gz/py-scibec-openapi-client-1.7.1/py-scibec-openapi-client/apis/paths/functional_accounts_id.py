from py-scibec-openapi-client.paths.functional_accounts_id.get import ApiForget
from py-scibec-openapi-client.paths.functional_accounts_id.delete import ApiFordelete
from py-scibec-openapi-client.paths.functional_accounts_id.patch import ApiForpatch


class FunctionalAccountsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
