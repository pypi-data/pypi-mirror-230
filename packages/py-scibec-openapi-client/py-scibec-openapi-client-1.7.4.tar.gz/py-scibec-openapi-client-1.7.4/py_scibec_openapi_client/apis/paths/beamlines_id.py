from py_scibec_openapi_client.paths.beamlines_id.get import ApiForget
from py_scibec_openapi_client.paths.beamlines_id.delete import ApiFordelete
from py_scibec_openapi_client.paths.beamlines_id.patch import ApiForpatch


class BeamlinesId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
