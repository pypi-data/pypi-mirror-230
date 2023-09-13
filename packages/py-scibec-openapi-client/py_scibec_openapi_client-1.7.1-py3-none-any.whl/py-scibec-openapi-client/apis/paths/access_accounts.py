from py-scibec-openapi-client.paths.access_accounts.get import ApiForget
from py-scibec-openapi-client.paths.access_accounts.post import ApiForpost
from py-scibec-openapi-client.paths.access_accounts.patch import ApiForpatch


class AccessAccounts(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
