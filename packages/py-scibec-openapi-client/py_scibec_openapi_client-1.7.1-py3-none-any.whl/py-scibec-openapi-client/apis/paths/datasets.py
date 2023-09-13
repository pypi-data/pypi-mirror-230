from py-scibec-openapi-client.paths.datasets.get import ApiForget
from py-scibec-openapi-client.paths.datasets.post import ApiForpost
from py-scibec-openapi-client.paths.datasets.patch import ApiForpatch


class Datasets(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
