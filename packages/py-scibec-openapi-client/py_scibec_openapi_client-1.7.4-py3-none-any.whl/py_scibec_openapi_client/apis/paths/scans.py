from py_scibec_openapi_client.paths.scans.get import ApiForget
from py_scibec_openapi_client.paths.scans.post import ApiForpost
from py_scibec_openapi_client.paths.scans.patch import ApiForpatch


class Scans(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
