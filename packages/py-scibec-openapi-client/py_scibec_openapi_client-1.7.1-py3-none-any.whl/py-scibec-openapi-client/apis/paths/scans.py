from py-scibec-openapi-client.paths.scans.get import ApiForget
from py-scibec-openapi-client.paths.scans.post import ApiForpost
from py-scibec-openapi-client.paths.scans.patch import ApiForpatch


class Scans(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
