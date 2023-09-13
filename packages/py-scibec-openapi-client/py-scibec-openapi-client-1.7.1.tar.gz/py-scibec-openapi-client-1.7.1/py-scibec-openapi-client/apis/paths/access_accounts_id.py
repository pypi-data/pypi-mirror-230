from py-scibec-openapi-client.paths.access_accounts_id.get import ApiForget
from py-scibec-openapi-client.paths.access_accounts_id.delete import ApiFordelete
from py-scibec-openapi-client.paths.access_accounts_id.patch import ApiForpatch


class AccessAccountsId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
