from py_scibec_openapi_client.paths.beamlines.get import ApiForget
from py_scibec_openapi_client.paths.beamlines.post import ApiForpost
from py_scibec_openapi_client.paths.beamlines.patch import ApiForpatch


class Beamlines(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
