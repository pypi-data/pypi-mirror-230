from py_scibec_openapi_client.paths.experiments.get import ApiForget
from py_scibec_openapi_client.paths.experiments.post import ApiForpost
from py_scibec_openapi_client.paths.experiments.patch import ApiForpatch


class Experiments(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
