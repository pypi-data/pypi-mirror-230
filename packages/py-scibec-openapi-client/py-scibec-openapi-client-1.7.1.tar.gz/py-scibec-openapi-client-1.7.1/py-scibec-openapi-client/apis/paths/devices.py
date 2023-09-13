from py-scibec-openapi-client.paths.devices.get import ApiForget
from py-scibec-openapi-client.paths.devices.post import ApiForpost
from py-scibec-openapi-client.paths.devices.patch import ApiForpatch


class Devices(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
