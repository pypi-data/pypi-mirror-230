from py_scibec_openapi_client.paths.devices.get import ApiForget
from py_scibec_openapi_client.paths.devices.post import ApiForpost
from py_scibec_openapi_client.paths.devices.patch import ApiForpatch


class Devices(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
