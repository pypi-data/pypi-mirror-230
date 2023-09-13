from py-scibec-openapi-client.paths.events.get import ApiForget
from py-scibec-openapi-client.paths.events.post import ApiForpost
from py-scibec-openapi-client.paths.events.patch import ApiForpatch


class Events(
    ApiForget,
    ApiForpost,
    ApiForpatch,
):
    pass
