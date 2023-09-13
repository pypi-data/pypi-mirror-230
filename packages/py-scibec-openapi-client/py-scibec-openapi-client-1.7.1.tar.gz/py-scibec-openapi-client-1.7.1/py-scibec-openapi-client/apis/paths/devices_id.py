from py-scibec-openapi-client.paths.devices_id.get import ApiForget
from py-scibec-openapi-client.paths.devices_id.delete import ApiFordelete
from py-scibec-openapi-client.paths.devices_id.patch import ApiForpatch


class DevicesId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
