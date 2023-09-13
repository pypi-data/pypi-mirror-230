from py_scibec_openapi_client.paths.access_configs.get import ApiForget
from py_scibec_openapi_client.paths.access_configs.post import ApiForpost
from py_scibec_openapi_client.paths.access_configs.patch import ApiForpatch


class AccessConfigs(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
