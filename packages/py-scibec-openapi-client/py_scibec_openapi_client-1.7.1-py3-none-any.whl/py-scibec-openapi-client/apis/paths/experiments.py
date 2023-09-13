from py-scibec-openapi-client.paths.experiments.get import ApiForget
from py-scibec-openapi-client.paths.experiments.post import ApiForpost
from py-scibec-openapi-client.paths.experiments.patch import ApiForpatch


class Experiments(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
