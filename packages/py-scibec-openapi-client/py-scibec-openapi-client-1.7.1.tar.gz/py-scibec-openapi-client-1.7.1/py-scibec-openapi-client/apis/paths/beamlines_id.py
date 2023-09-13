from py-scibec-openapi-client.paths.beamlines_id.get import ApiForget
from py-scibec-openapi-client.paths.beamlines_id.delete import ApiFordelete
from py-scibec-openapi-client.paths.beamlines_id.patch import ApiForpatch


class BeamlinesId(
    ApiForget,
    ApiFordelete,
    ApiForpatch,
):
    pass
