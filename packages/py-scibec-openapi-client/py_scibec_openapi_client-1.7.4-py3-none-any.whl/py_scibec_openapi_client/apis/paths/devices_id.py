from py_scibec_openapi_client.paths.devices_id.get import ApiForget
from py_scibec_openapi_client.paths.devices_id.delete import ApiFordelete
from py_scibec_openapi_client.paths.devices_id.patch import ApiForpatch


class DevicesId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
