from py-scibec-openapi-client.paths.scans_id.get import ApiForget
from py-scibec-openapi-client.paths.scans_id.delete import ApiFordelete
from py-scibec-openapi-client.paths.scans_id.patch import ApiForpatch


class ScansId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
