from py-scibec-openapi-client.paths.experiment_accounts.get import ApiForget
from py-scibec-openapi-client.paths.experiment_accounts.post import ApiForpost
from py-scibec-openapi-client.paths.experiment_accounts.patch import ApiForpatch


class ExperimentAccounts(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
