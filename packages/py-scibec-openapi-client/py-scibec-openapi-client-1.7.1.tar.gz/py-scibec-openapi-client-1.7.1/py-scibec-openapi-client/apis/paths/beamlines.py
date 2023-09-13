from py-scibec-openapi-client.paths.beamlines.get import ApiForget
from py-scibec-openapi-client.paths.beamlines.post import ApiForpost
from py-scibec-openapi-client.paths.beamlines.patch import ApiForpatch


class Beamlines(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
