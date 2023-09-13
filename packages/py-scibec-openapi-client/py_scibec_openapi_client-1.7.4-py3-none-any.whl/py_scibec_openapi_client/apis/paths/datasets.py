from py_scibec_openapi_client.paths.datasets.get import ApiForget
from py_scibec_openapi_client.paths.datasets.post import ApiForpost
from py_scibec_openapi_client.paths.datasets.patch import ApiForpatch


class Datasets(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
