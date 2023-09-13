from py_scibec_openapi_client.paths.scans_id.get import ApiForget
from py_scibec_openapi_client.paths.scans_id.delete import ApiFordelete
from py_scibec_openapi_client.paths.scans_id.patch import ApiForpatch


class ScansId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
