from py-scibec-openapi-client.paths.functional_accounts.get import ApiForget
from py-scibec-openapi-client.paths.functional_accounts.post import ApiForpost
from py-scibec-openapi-client.paths.functional_accounts.patch import ApiForpatch


class FunctionalAccounts(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
